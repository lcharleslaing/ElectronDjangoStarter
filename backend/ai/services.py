import os
from openai import OpenAI

def get_openai():
    key = os.getenv("OPENAI_API_KEY")
    return OpenAI(api_key=key) if key else None
