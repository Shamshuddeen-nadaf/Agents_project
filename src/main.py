import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import warnings
from pydantic import PydanticDeprecatedSince20

# Suppress the specific deprecation warning from Pydantic
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

from src.graph.builder import build_agent
from langchain_core.messages import HumanMessage

def run_agent(question: str):
    agent = build_agent()
    state = {
        "messages": [HumanMessage(content=question).dict()],
        "plan": None,
        "current_step": 0,
        "tool_results": [],
        "final_answer": None
    }
    result = agent.invoke(state) # type: ignore
    print("\nLLM : Final answer:", result["final_answer"])

if __name__ == "__main__":
    # Test with a simple GAIA Level 1 question
    filePath = r"FILES\ASSOCIATE.pdf"
    run_agent(f"What is in the file {filePath} talking about?")