from typing_extensions import Literal
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from functools import lru_cache
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
OLLAMA_CONFIG = {
    "model": "qwen2:7b",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
}

LM_STUDIO_CONFIG = {
    "model": "meta-llama-3-8b-instruct",
    "base_url": "http://localhost:1234/v1",
    "api_key": "not-needed",
    "temperature": 0.7,
}

GEMINI_CONFIG = {
    "model":"gemini-2.5-flash",
    "api_key":os.getenv("GEMINI_API_KEY"),
    "temperature":0.7
}
@lru_cache(maxsize=1)
def get_llm(provider:Literal["lm_studio","ollama","gemini"]  = "gemini"):
    if provider == "ollama":
        return ChatOllama(**OLLAMA_CONFIG)
    elif provider == "lm_studio":
        return ChatOpenAI(**LM_STUDIO_CONFIG)
    else:
        return ChatGoogleGenerativeAI(**GEMINI_CONFIG)

