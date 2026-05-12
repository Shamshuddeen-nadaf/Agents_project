from langchain_ollama import ChatOllama

LLM_CONFIG = {
    "model": "qwen2:7b",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
}

def get_llm():
    return ChatOllama(**LLM_CONFIG)
