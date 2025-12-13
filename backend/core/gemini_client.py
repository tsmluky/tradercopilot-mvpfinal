import os
import google.generativeai as genai
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    """
    Client for interacting with Google's Gemini AI models.
    """
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. GeminiClient will not function.")
            return

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def generate_content(self, prompt: str) -> Optional[str]:
        """
        Generates content based on a text prompt.
        """
        if not self.api_key:
            logger.error("Attempted to generate content without GEMINI_API_KEY")
            return None

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return None

    def generate_chat(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """
        Simulates a chat interaction. 
        Note: The native SDK has a chat session object, but for stateless API usage 
        we might just concatenate or use the chat interface if needed.
        For now, we'll adapt list of messages to a prompt or use chat history.
        """
        if not self.api_key:
            return None
            
        try:
            # Simple conversion for single turn or managed history
            # For a proper chat session, we should use model.start_chat()
            # But here we likely get a full history list.
            
            chat = self.model.start_chat(history=[]) 
            # We might need to map 'role': 'user'/'assistant' to SDK format if we want history
            # SDK expects history as [{'role': 'user', 'parts': ['...']}, ...]
            # 'system' role is not fully supported in standard chat history in 1.0, 
            # usually provided as system instruction in 1.5.
            
            # For simplicity in this v1 implementation, we will just send the last message
            # if we are not maintaining state here. 
            # OR better: Construct a full prompt if we are stateless.
            
            # Let's assume messages is [{'role': 'user', 'content': '...'}, ...]
            last_message = messages[-1]['content']
            response = chat.send_message(last_message)
            return response.text
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            return None
