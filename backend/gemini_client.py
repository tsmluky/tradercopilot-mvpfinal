from __future__ import annotations
import os
import google.generativeai as genai

# ==================================================================================
# Gemini Client
# ==================================================================================
# Utiliza google-generativeai para conectar con Gemini 1.5 Flash (recomendado para demos).
# Requiere GEMINI_API_KEY en el entorno.

GEMINI_MODEL = "gemini-2.5-flash"

def _configure_genai():
    """
    Configura la API key de Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback a DEEPSEEK_API_KEY si el usuario reusa la variable, 
        # aunque lo ideal es que configure GEMINI_API_KEY.
        api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        print("[Gemini] ERROR: GEMINI_API_KEY not found in environment.")
        return False
        
    genai.configure(api_key=api_key)
    return True

def generate_pro(prompt: str) -> str:
    """
    Genera el análisis PRO utilizando Gemini 1.5 Flash.
    """
    if not _configure_genai():
        return prompt # Fallback a devolver el prompt si no hay key

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # System instructions se pasan mejor en el prompt para Flash o usando system_instruction en la config,
        # pero para simplicidad y "Wow" factor rápido, lo inyectamos como contexto.
        
        # En la API de python de genai, el 'system prompt' se puede configurar al crear el modelo,
        # pero aquí vamos a mantenerlo simple y directo.
        
        system_instruction = (
            "Eres TraderCopilot, un analista técnico de élite institucional y asesor de posiciones para trading.\n"
            "Tu objetivo es impresionar al usuario con la profundidad y claridad de tu análisis.\n"
            "Debes responder SIEMPRE ÚNICAMENTE con un bloque de texto formateado entre "
            "#ANALYSIS_START y #ANALYSIS_END, manteniendo las secciones requeridas: "
            "#CTXT# (Contexto de mercado), #TA# (Análisis Técnico Institucional), #PLAN# (Estrategia precisa), "
            "#INSIGHT# (Dato clave OnChain/Fundamental), #PARAMS# (Niveles exactos).\n"
            "El idioma de respuesta debe ser SIEMPRE ESPAÑOL (Castellano) de España, tono profesional, serio y directo al grano.\n"
            "Usa terminología técnica correcta (Order Blocks, FVG, Liquidez, Estructura de Mercado)."
        )

        full_prompt = f"{system_instruction}\n\nUSER REQUEST:\n{prompt}"
        
        response = model.generate_content(full_prompt)
        
        if response.text:
            print(f"[Gemini] generated {len(response.text)} chars.")
            return response.text
        else:
            print("[Gemini] Empty response.")
            return prompt

    except Exception as e:
        print(f"[Gemini] Error generating content: {e}")
        return prompt

def generate_chat(messages: list[dict]) -> str:
    """
    Maneja el chat del Advisor con historial.
    """
    if not _configure_genai():
        return "Error: GEMINI_API_KEY not configured."

    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Convertir mensajes al formato de Gemini si es necesario, 
        # pero para Flash podemos concatenar historial como contexto si chat session es compleja.
        # Aquí iniciaremos un chat session nuevo con el historial.
        
        # Mapping simple de roles:
        # system -> user (Gemini no soporta system message en historial estricto a veces en v1beta, mejor inyectar)
        # user -> user
        # assistant -> model
        
        gemini_history = []
        
        system_prompt = (
             "Eres el Asesor de Riesgo de TraderCopilot (Risk Advisor AI). Ayudas a los traders a gestionar el riesgo, "
            "sugerir ajustes de posición y analizar escenarios de mercado.\n"
            "Sé conciso, profesional y directo. Céntrate en la gestión de riesgos (RR, tamaño de posición, SL/TP).\n"
            "NO des consejos financieros, solo análisis técnico y escenarios de riesgo.\n"
            "Responde SIEMPRE en ESPAÑOL (Castellano)."
        )
        
        # Inyectar system prompt en el primer mensaje
        if messages:
            first_msg = messages[0]
            first_msg['content'] = system_prompt + "\n\n" + first_msg['content']
        else:
             messages = [{'role': 'user', 'content': system_prompt}]
             
        # Construir historial para chat
        chat = model.start_chat(history=[])
        
        last_content = ""
        for m in messages:
            role = 'user' if m['role'] in ['user', 'system'] else 'model'
            # Gemini python lib maneja el estado internamente con send_message, 
            # no rellenando history manualmente tan facil si no son pares user/model estrictos.
            # Metodo robusto: Enviar todo como un unico prompt "Chat Transcript" si es corto, 
            # o intentar reconstruir. Para demo flash, lo más seguro es enviar el ultimo mensaje con contexto.
            pass

        # Estrategia simplificada: Enviar todo el contexto como un solo prompt para asegurar coherencia
        # ya que la gestion de historial de Gemini puede ser estricta con el turno user/model.
        transcript = f"System: {system_prompt}\n"
        for m in messages:
             transcript += f"{m['role'].capitalize()}: {m['content']}\n"
        
        transcript += "Assistant:"
        
        response = model.generate_content(transcript)
        return response.text
        
    except Exception as e:
        print(f"[Gemini] Chat Error: {e}")
        return f"Error conectando con Advisor (Gemini): {str(e)}"
