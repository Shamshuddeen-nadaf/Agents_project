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
_THICK_LINE = '=' * 60

if __name__ == "__main__":
    try:
        app = build_graph()
        png_bytes = app.get_graph().draw_mermaid_png()
        with open('./graph.png','wb') as f:
            f.write(png_bytes)
        print("Graph built successfully.\n")

        state = make_initial_state("Plan out a trip to Mangalore starting from the Badami Cave Temples.")

        for event in app.stream(state):
            for node_name, node_state in event.items():
                print(f"\n{_THICK_LINE}")
                print(f"  NODE: {node_name}")
                print(_THICK_LINE)

                if node_name == "router":
                    print(f"  Status → {node_state.get('status')}")
                    msgs = node_state.get('messages', [])
                    if msgs:
                        last = msgs[-1]
                        text = last.content[:500] if hasattr(last, 'content') else str(last)
                        print(f"  Thought: {text}")

                elif node_name == "planner":
                    print(f"  Plan:")
                    for step in node_state.get('plan', []):
                        print(f"    {step['id']}: {step['description']}")
                    print(f"  Next: {node_state.get('current_step_id')}")

                elif node_name == "reasoner":
                    trace = node_state.get('reasoning_trace', [])
                    if trace:
                        t = trace[-1]
                        print(f"  Strategy: {t['strategy']}  (confidence: {t['confidence']})")
                        print(f"  Thought:\n    {t['thought'][:600]}")

                elif node_name == "tool_node":
                    for msg in node_state.get('messages', []):
                        if hasattr(msg, 'name'):
                            print(f"  Tool called: {msg.name}")
                        content = getattr(msg, 'content', None)
                        if content:
                            print(f"  Result: {str(content)[:300]}")

                elif node_name == "critic":
                    critiques = node_state.get('critiques', [])
                    if critiques:
                        c = critiques[-1]
                        print(f"  Critique [{c['severity']}]: {c['critique'][:300]}")
                    print(f"  Status → {node_state.get('status')}")

                elif node_name == "memory":
                    facts = node_state.get('verified_facts', [])
                    print(f"  Stored {len(facts)} new facts")

                print(f"  Iteration: {node_state.get('iteration')}  |  "
                      f"Step: {node_state.get('current_step_id')}  |  "
                      f"Status: {node_state.get('status')}")

        final = event

        print(f"\n{_THICK_LINE}")
        print("  FINAL RESULT")
        print(f"{_THICK_LINE}")
        print("Final status:", final.get("status"))

        if final.get("final_answer"):
            print("Answer:", final["final_answer"])
        elif final.get("messages"):
            last = final["messages"][-1]
            text = last.content[:500] if hasattr(last, "content") else str(last)
            print("Last message:", text)
        else:
            print("No answer generated.")

        if final.get("plan"):
            print("Plan steps:")
            for s in final["plan"]:
                print(f"  {s['id']}: {s['description']} [{s['status']}]")
        if final.get("error"):
            print("Error:", final["error"])
    except Exception as e:
        print(f"Error: {e}")


