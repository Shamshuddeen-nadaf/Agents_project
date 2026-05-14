import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.graph.graphbuilder import build_graph
from src.graph.state import AgentState
from langchain_core.messages import HumanMessage

def make_initial_state(task: str) -> AgentState:
    return {
        "messages": [HumanMessage(content=task)],
        "iteration": 0,
        "max_iterations": 20,
        "task": task,
        "status": "planning",
        "reasoning_trace": [],
        "current_strategy": "",
        "confidence_score": 0.0,
        "uncertainty_flags": [],
        "plan": [],
        "current_step_id": "",
        "replan_count": 0,
        "replan_reasons": [],
        "action_history": [],
        "failed_tools": [],
        "working_memory": {},
        "episodic_memory": [],
        "entity_map": {},
        "hypotheses": [],
        "verified_facts": [],
        "contradictions": [],
        "critiques": [],
        "retry_count": 0,
        "max_retries_per_step": 3,
        "backtrack_to_step": None,
        "retrieved_documents": [],
        "external_context": {},
        "constraints": [],
        "time_budget_ms": None,
        "intermediate_answers": [],
        "final_answer": None,
        "answer_confidence": 0.0,
        "citations": [],
        "error": None,
    }

if __name__ == "__main__":
    try:
        app = build_graph()
        png_bytes = app.get_graph().draw_mermaid_png()
        with open('./graph.png','wb') as f:
            f.write(png_bytes)
        print("Graph built successfully.")
        print()

        state = make_initial_state("What is the capital of France?")
        result = app.invoke(state)
        print("Final status:", result.get("status"))
        print()

        if result.get("final_answer"):
            print("Answer:", result["final_answer"])
        elif result.get("messages"):
            last = result["messages"][-1]
            print("Last message:", last.content[:500] if hasattr(last, "content") else last)
        else:
            print("No answer generated.")
        print()

        if result.get("plan"):
            print("Plan steps:")
            for s in result["plan"]:
                print(f"  {s['id']}: {s['description']} [{s['status']}]")
        if result.get("error"):
            print("Error:", result["error"])
    except Exception as e:
        print(f"Error: {e}")
