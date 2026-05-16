from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

LLM_CONFIG = {
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

def get_llm(provider: str = "lm_studio"):
    if provider == "ollama":
        return ChatOllama(**LLM_CONFIG)
    return ChatOpenAI(**LM_STUDIO_CONFIG)
