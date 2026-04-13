from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

# 🔥 ADD THIS (must be here, not just in app.py)
load_dotenv()

def get_llm():
    api_key = os.getenv("OPENROUTER_API_KEY")
    print("DEBUG KEY:", api_key)  # temporary debug

    return ChatOpenAI(
        model="openai/gpt-4o-mini",
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        temperature=0.2
    )