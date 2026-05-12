'''
This file is to take the nodes and build the graph.
Connections done here should make a function to return a compiled graph
'''
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.graph.state import AgentState
from src.graph.nodes import router_node, planner_node, reasoner_node, critic_node, memory_node
from src.tools.web_search import web_search
from src.tools.calculator import calculator
from src.tools.file_reader import file_reader
from src.tools.web_scraper import web_scraper_tool


def _route_router(state: AgentState) -> str:
    return "planner" if state["status"] == "planning" else END


def _route_reasoner(state: AgentState) -> str:
    return END if state["status"] == "done" else "tool_node"


def _route_critic(state: AgentState) -> str:
    return "planner" if state["status"] == "replanning" else "memory"


def build_graph():
    tools = [web_search, calculator, file_reader, web_scraper_tool]

    workflow = StateGraph(AgentState)

    workflow.add_node("router", router_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("reasoner", reasoner_node)
    workflow.add_node("tool_node", ToolNode(tools))
    workflow.add_node("critic", critic_node)
    workflow.add_node("memory", memory_node)

    workflow.add_edge(START, "router")

    workflow.add_conditional_edges("router", _route_router, {
        "planner": "planner",
        END: END,
    })

    workflow.add_edge("planner", "reasoner")

    workflow.add_conditional_edges("reasoner", _route_reasoner, {
        "tool_node": "tool_node",
        END: END,
    })

    workflow.add_edge("tool_node", "critic")

    workflow.add_conditional_edges("critic", _route_critic, {
        "planner": "planner",
        "memory": "memory",
    })

    workflow.add_edge("memory", "reasoner")

    return workflow.compile()
