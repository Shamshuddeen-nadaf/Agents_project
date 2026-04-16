import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes import router_node, planner_node, executor_node, answer_node

def build_agent():
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("answer", answer_node)

    # Set entry point
    graph.set_entry_point("router")

    # Conditional edges from router
    graph.add_conditional_edges(
        "router",
        lambda state: state.get("next_action", "answer"),
        {"plan": "planner", "answer": "answer"}
    )

    # After planner, go to executor
    graph.add_edge("planner", "executor")

    # After executor, either go back to executor (if more steps) or to answer
    def after_executor(state):
        plan = state.get("plan", "")
        step = state.get("current_step", 0)
        total_steps = len([l for l in plan.split("\n") if l.strip() and 
                      ("[web_search]" in l or "[calculator]" in l or "[file_reader]" in l)])  # ← added file_reader
        if step < total_steps:
            return "executor"
        else:
            return "answer"
    graph.add_conditional_edges("executor", after_executor, {"executor": "executor", "answer": "answer"})

    graph.add_edge("answer", END)

    return graph.compile()

if __name__ == '__main__':
    agent_test = build_agent()
    agent_test.get_graph().draw_mermaid_png()
    image_path = os.path.join(project_root,"graph.png")
    with open(image_path,'wb') as f:
        f.write(agent_test.get_graph().draw_mermaid_png())
    print(f"Saved in root/graph.png")