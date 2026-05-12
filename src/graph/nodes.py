'''
This is file which has the nodes for the graph and their operations.
'''
import json
import re
from datetime import datetime
from src.graph.state import AgentState, PlanStep, SelfCritique, MemoryEntry, ReasoningTrace
from src.llm import get_llm
from langchain_core.messages import ToolMessage
from src.tools.web_search import web_search
from src.tools.calculator import calculator
from src.tools.file_reader import file_reader
from src.tools.web_scraper import web_scraper_tool

tools = [web_search, calculator, file_reader, web_scraper_tool]
llm = get_llm()
bound_llm = llm.bind_tools(tools)
# helper functions
def _extract_json(text: str) -> str:
    '''Pull the first JSON array out of whatever the LLM blurted out'''
    match = re.search(r'\[.*\]', text, re.DOTALL)
    return match.group() if match else text.strip()


def parse_plan(raw: str) -> list[PlanStep]:
    '''Turn LLM text into a list of PlanStep objects'''
    try:
        steps = json.loads(_extract_json(raw))
    except json.JSONDecodeError:
        return [PlanStep(id="step_1", description=raw[:200], depends_on=[], status="pending", result=None)]
    return [
        PlanStep(id=s.get("id", f"step_{i+1}"), description=s.get("description", ""),
                 depends_on=s.get("depends_on", []), status="pending", result=None)
        for i, s in enumerate(steps)
    ]


def parse_critique(raw: str) -> SelfCritique:
    '''Extract a critique from the LLM output — severity, what went wrong, what to do about it'''
    severity = "medium"
    if "high" in raw.lower():
        severity = "high"
    elif "low" in raw.lower():
        severity = "low"
    return SelfCritique(
        step=0,
        critique=raw[:500],
        severity=severity,
        action_taken="logged",
    )


def parse_facts(raw: str) -> list[MemoryEntry]:
    '''Turn LLM output into memory entries. Simple split-by-line approach.'''
    lines = [l.strip() for l in raw.split("\n") if l.strip()]
    facts = []
    for line in lines[:10]:
        facts.append(MemoryEntry(
            key=line.split(":")[0] if ":" in line else f"fact_{len(facts)}",
            value=line,
            source="llm",
            confidence=0.7,
            created_at=datetime.now().isoformat(),
        ))
    return facts

def planner_node(state: AgentState) -> AgentState:
    '''Ask the LLM to break the task into steps, then store the plan'''
    prompt = f"""Task: {state['task']}
Constraints: {state.get('constraints', [])}
Known facts: {state.get('verified_facts', [])}
Previous failures: {state.get('replan_reasons', [])}"""
    state["plan"] = parse_plan(llm.invoke(prompt).content)
    state["status"] = "executing"
    state["current_step_id"] = "step_1" if state["plan"] else ""
    return state


def reasoner_node(state: AgentState) -> AgentState:
    '''Look at the current step and figure out what tool to call, if any'''

    # grab the step we're supposed to be working on
    current_step = next(
        (s for s in state.get("plan", []) if s["id"] == state.get("current_step_id")),
        None,
    )
    if not current_step:
        state["status"] = "done"
        return state

    thought = bound_llm.invoke(f"""Goal: {current_step['description']}
Working memory: {state.get('working_memory', {})}
Action history: {state.get('action_history', [])}
Active hypotheses: {state.get('hypotheses', [])}
Confidence so far: {state.get('confidence_score', 0.0)}

Select the right tool for the job and provide the input.""")

    state["messages"].append(thought)
    state["reasoning_trace"].append(ReasoningTrace(
        step=state.get("iteration", 0),
        thought=thought.content,
        confidence=0.5,
        strategy="react",
        timestamp=datetime.now().isoformat(),
    ))
    return state

def critic_node(state: AgentState) -> AgentState:
    '''Check the last action — was it useful? Should we backtrack or keep going?'''

    tool_msgs = [m for m in reversed(state.get("messages", [])) if isinstance(m, ToolMessage)]
    if not tool_msgs:
        state["status"] = "executing"
        return state

    last_result = tool_msgs[0].content

    critique = llm.invoke(f"""Last tool result: {last_result}
Your hypothesis was: {state['hypotheses']}

Did this advance the goal? Rate confidence 0–1.
If confidence < 0.4, recommend backtracking to which step.
Identify any contradictions with verified facts.""")

    parsed = parse_critique(critique.content)
    state["critiques"].append(parsed)

    if parsed["severity"] == "high":
        state["status"] = "replanning"
        state["replan_reasons"].append(parsed["critique"])
    else:
        state["status"] = "executing"

    return state

def memory_node(state: AgentState) -> AgentState:
    '''Pull key facts out of tool results and stash them in long-term memory'''

    tool_msgs = [m for m in reversed(state.get("messages", [])) if isinstance(m, ToolMessage)]
    if not tool_msgs:
        return state

    new_facts = llm.invoke(f"""From this result: {tool_msgs[0].content}
Extract key facts, entities, and relationships as JSON.
Flag confidence for each.""")

    facts = parse_facts(new_facts.content)
    state["episodic_memory"].extend(facts)
    state["verified_facts"].extend(f["value"] for f in facts if f["confidence"] > 0.85)

    plan_ids = [s["id"] for s in state.get("plan", [])]
    current_idx = plan_ids.index(state["current_step_id"]) if state["current_step_id"] in plan_ids else -1
    if current_idx + 1 < len(plan_ids):
        state["current_step_id"] = plan_ids[current_idx + 1]
    else:
        state["status"] = "done"
    return state


def router_node(state: AgentState) -> AgentState:
    '''Figure out if this task needs the full planner pipeline or can be answered directly'''

    classification = llm.invoke(f"""Task: {state['task']}

Is this a simple question (answer directly with one tool call or no tools)
or a complex task (needs multi-step planning)?
Reply with exactly one word: "simple" or "complex\"""")

    if "simple" in classification.content.lower():
        answer = llm.invoke(f"Answer this question concisely: {state['task']}")
        state["messages"].append(answer)
        state["final_answer"] = answer.content
        state["status"] = "done"
    else:
        state["status"] = "planning"
    return state