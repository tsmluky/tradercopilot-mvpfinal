import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv("backend/.env")
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
genai.configure(api_key=api_key)

print("--- AVAILABLE MODELS ---")
for m in genai.list_models():
    if "gemini" in m.name:
        print(f"Name: {m.name} | Methods: {m.supported_generation_methods}")
print("--- END ---")
