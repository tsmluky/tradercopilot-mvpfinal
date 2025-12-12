
from __future__ import annotations
import os
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import google.generativeai as genai

# === ABSTRACTION LAYER ===

class AIProvider(ABC):
    """Interfaz abstracta para proveedores de IA."""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], system_instruction: str = None) -> str:
        """
        Genera una respuesta de chat.
        
        Args:
            messages: Lista de mensajes [{"role": "user", "content": "..."}]
            system_instruction: Instrucción opcional del sistema.
        """
        pass

    @abstractmethod
    def generate_analysis(self, prompt: str, system_instruction: str = None) -> str:
        """
        Genera un análisis técnico (one-shot).
        """
        pass


# === DEEPSEEK IMPLEMENTATION (Legacy/Cost-Effective) ===

class DeepSeekProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "")
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

    def chat(self, messages: List[Dict[str, str]], system_instruction: str = None) -> str:
        if not self.api_key:
            return "Error: DEEPSEEK_API_KEY no configurada."

        # Inyectar system message si existe
        full_messages = []
        if system_instruction:
            full_messages.append({"role": "system", "content": system_instruction})
        
        full_messages.extend(messages)

        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            resp = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            return f"DeepSeek Error: {resp.status_code} - {resp.text[:100]}"
        except Exception as e:
            return f"DeepSeek Connection Error: {str(e)}"

    def generate_analysis(self, prompt: str, system_instruction: str = None) -> str:
        # Reutilizamos la lógica de chat para one-shot
        return self.chat([{"role": "user", "content": prompt}], system_instruction)


# === GEMINI IMPLEMENTATION (Multimodal/High-Logic) ===

class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        # Gemini 1.5 Flash es el mejor balance costo/velocidad en Free Tier
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def chat(self, messages: List[Dict[str, str]], system_instruction: str = None) -> str:
        if not self.api_key:
            return "Error: GEMINI_API_KEY no configurada. Añádela al .env"

        try:
            # Configurar modelo con system instruction
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            
            # Convertir historial al formato de Gemini
            # Gemini usa 'user' y 'model' (en lugar de 'assistant')
            gemini_history = []
            
            # Si el último mensaje es del usuario, ese es el prompt actual, el resto es historia
            user_message = messages[-1]["content"]
            history_messages = messages[:-1]
            
            for msg in history_messages:
                role = "user" if msg["role"] == "user" else "model"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
                
            chat_session = model.start_chat(history=gemini_history)
            response = chat_session.send_message(user_message)
            
            return response.text
            
        except Exception as e:
            return f"Gemini Error: {str(e)}"

    def generate_analysis(self, prompt: str, system_instruction: str = None) -> str:
        if not self.api_key:
            return "Error: GEMINI_API_KEY no configurada."
            
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini Analysis Error: {str(e)}"


# === FACTORY ===

def get_ai_service() -> AIProvider:
    """
    Retorna el proveedor configurado en .env (AI_PROVIDER).
    Default: 'gemini' (Si hay key), sino 'deepseek'.
    """
    # Preferencia del usuario
    provider = os.getenv("AI_PROVIDER", "auto").lower()
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    
    if provider == "gemini":
        return GeminiProvider()
    elif provider == "deepseek":
        return DeepSeekProvider()
    
    # Auto-selección: Preferimos Gemini si hay key (Free Tier potente)
    if gemini_key:
        print("[AI Service] Auto-selecting: Gemini")
        return GeminiProvider()
    elif deepseek_key:
        print("[AI Service] Auto-selecting: DeepSeek")
        return DeepSeekProvider()
    
    # Fallback dummy si no hay nada
    print("[AI Service] ⚠️ NO KEYS FOUND. Using Dummy Provider.")
    return DeepSeekProvider() # Retornará error de key faltante
