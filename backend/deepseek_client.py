from __future__ import annotations
import os
from typing import Any, Dict

import requests

raw_url = os.getenv("DEEPSEEK_API_URL", "")
if not raw_url.startswith("http"):
    DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
else:
    DEEPSEEK_API_URL = raw_url

DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def _load_env_from_file() -> None:
    """
    Si la API key no está en el entorno, intenta cargar backend/.env
    (mismo formato KEY=VALUE, líneas con # como comentarios).
    """
    if os.getenv("DEEPSEEK_API_KEY"):
        return  # ya está cargada

    backend_dir = os.path.dirname(__file__)
    dotenv_path = os.path.join(backend_dir, ".env")
    if not os.path.exists(dotenv_path):
        print(f"[DeepSeek] .env no encontrado en {dotenv_path}")
        return

    print(f"[DeepSeek] Cargando .env desde {dotenv_path}")
    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k:
                    os.environ.setdefault(k, v)
        print("[DeepSeek] .env cargado en proceso (variables básicas)")
    except Exception as e:
        print(f"[DeepSeek] Error cargando .env: {e!r}")


def _build_payload(prompt: str) -> Dict[str, Any]:
    """
    Construye el payload para DeepSeek usando el prompt PRO ya formateado
    (#ANALYSIS_START..#ANALYSIS_END).
    """
    temperature_str = os.getenv("DEEPSEEK_TEMPERATURE", "0.6")
    max_tokens_str = os.getenv("DEEPSEEK_MAX_TOKENS", "1400")

    try:
        temperature = float(temperature_str)
    except ValueError:
        temperature = 0.6

    try:
        max_tokens = int(max_tokens_str)
    except ValueError:
        max_tokens = 1400

    return {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Eres TraderCopilot, un analista técnico y asesor de posiciones para trading.\n"
                    "Debes responder SIEMPRE ÚNICAMENTE con un bloque de texto entre "
                    "#ANALYSIS_START y #ANALYSIS_END, manteniendo exactamente las secciones "
                    "#CTXT#, #TA#, #PLAN#, #INSIGHT#, #PARAMS#.\n"
                    "El idioma de respuesta debe ser SIEMPRE ESPAÑOL (Castellano).\n"
                    "No añadas texto fuera de ese bloque. No expliques el formato."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def generate_pro(prompt: str) -> str:
    """
    Envía el prompt PRO a DeepSeek y devuelve el análisis generado.

    Si falta la API key o algo falla, devuelve el prompt original como fallback
    para no romper el endpoint /analyze/pro.
    Además, escribe trazas mínimas en consola para poder depurar.
    """
    # 1) Asegurar que intentamos cargar backend/.env si hace falta
    _load_env_from_file()

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        print("[DeepSeek] DEEPSEEK_API_KEY vacío o no encontrado. Devolviendo prompt (modo plantilla).")
        return prompt

    payload = _build_payload(prompt)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"[DeepSeek] Llamando a {DEEPSEEK_API_URL} con modelo={DEEPSEEK_MODEL}")
    try:
        resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=40)
    except Exception as e:
        print(f"[DeepSeek] Error de red al llamar a API: {e!r}. Devolviendo prompt.")
        return prompt

    if resp.status_code != 200:
        text_preview = resp.text[:300].replace("\\n", " ")
        print(f"[DeepSeek] Respuesta HTTP no-200: {resp.status_code} -> {text_preview!r}. Devolviendo prompt.")
        return prompt

    try:
        data = resp.json()
    except Exception as e:
        print(f"[DeepSeek] Error parseando JSON: {e!r}. Devolviendo prompt.")
        return prompt

    choices = data.get("choices") or []
    if not choices:
        print("[DeepSeek] JSON sin 'choices'. Devolviendo prompt.")
        return prompt

    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not content:
        print("[DeepSeek] 'message.content' vacío. Devolviendo prompt.")
        return prompt

    print("[DeepSeek] Respuesta recibida correctamente del modelo.")
    # Asumimos que el modelo ya devuelve el bloque con #ANALYSIS_START..#ANALYSIS_END.
    return content


def generate_chat(messages: list[dict]) -> str:
    """
    Envía un historial de mensajes de chat a DeepSeek y devuelve la respuesta.
    Usado para el Advisor Chat interactivo.
    """
    _load_env_from_file()
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    
    if not api_key:
        return "Error: DEEPSEEK_API_KEY not configured in backend."

    # System prompt para el chat
    system_msg = {
        "role": "system",
        "content": (
            "Eres el Asesor de Riesgo de TraderCopilot (Risk Advisor AI). Ayudas a los traders a gestionar el riesgo, "
            "sugerir ajustes de posición y analizar escenarios de mercado.\n"
            "Sé conciso, profesional y directo. Céntrate en la gestión de riesgos (RR, tamaño de posición, SL/TP).\n"
            "NO des consejos financieros, solo análisis técnico y escenarios de riesgo.\n"
            "Responde SIEMPRE en ESPAÑOL (Castellano)."
        )
    }
    
    # Construir payload con historial completo
    full_messages = [system_msg] + messages
    
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": full_messages,
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return content
        else:
            return f"Error from AI provider: {resp.status_code} - {resp.text[:100]}"
    except Exception as e:
        return f"Connection error: {str(e)}"
