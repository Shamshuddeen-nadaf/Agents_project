from src.graph.state import AgentState
from src.models.model_factory import get_llm
from src.tools.web_search import web_search
from src.tools.calculator import calculator
from src.tools.file_reader import file_reader
import json

llm = get_llm(use_local=True)  # change to True if using Ollama

def router_node(state: AgentState):
    """Decide if the question is simple (direct answer) or complex (needs planning)."""
    last_msg = state["messages"][-1]["content"]
    prompt = f"""Classify the user's question as 'simple' or 'complex'.
Simple: basic fact, math, or known info. Complex: needs web search, multi-step reasoning, external data, or FILE READING.
Question: {last_msg}
Answer with only the word 'simple' or 'complex'."""
    response = str(llm.invoke(prompt).content).strip().lower()
    return {"next_action": "answer" if response == "simple" else "plan"}

def planner_node(state: AgentState):
    """Create a numbered plan for complex questions including file operations."""
    question = state["messages"][-1]["content"]
    prompt = f"""You are an AI agent. For the question below, produce a step-by-step numbered plan.
Each step should be one of: [web_search], [calculator], [file_reader], or [final_answer].

[file_reader] - Use this when you need to read data from a file (CSV, TXT, PDF, etc.)
[web_search] - Use this for searching the internet
[calculator] - Use this for mathematical calculations
[final_answer] - Use this to provide the final response

Example plans:
1. [file_reader] data.csv
2. [calculator] sum of column 'sales'
3. [final_answer] Return the total sales

OR
1. [web_search] Who is the CEO of the company that makes the Pixel 7?
2. [final_answer] Return the name.

Question: {question}
Plan:"""
    plan = llm.invoke(prompt).content
    return {"plan": plan, "current_step": 0, "tool_results": []}

def executor_node(state: AgentState):
    """Execute the current step of the plan including file operations."""
    plan = state["plan"]
    step_num = state["current_step"] + 1
    lines = [l for l in str(plan).split("\n") if l.strip()]
    
    if step_num > len(lines):
        return {"current_step": step_num}  # no more steps

    current_line = lines[step_num-1]
    new_results = state.get("tool_results", [])
    
    # Parse step and execute appropriate tool
    if "[web_search]" in current_line:
        query = current_line.split("[web_search]")[-1].strip()
        result = web_search.invoke(query)
        new_results.append(f"Step {step_num} (web_search): {result}")
        
    elif "[calculator]" in current_line:
        expr = current_line.split("[calculator]")[-1].strip()
        result = calculator.invoke(expr)
        new_results.append(f"Step {step_num} (calculator): {result}")
        
    elif "[file_reader]" in current_line:
        # Extract file path from the step
        # Example: "[file_reader] data.csv" or "[file_reader] read file.csv"
        file_path = current_line.split("[file_reader]")[-1].strip()
        
        # Handle different formats
        if "read" in file_path.lower():
            # If format is "[file_reader] read data.csv"
            file_path = file_path.replace("read", "").strip()
        
        try:
            result = file_reader.invoke(file_path)  # Call your file_reader tool
            new_results.append(f"Step {step_num} (file_reader): {result}")
        except Exception as e:
            new_results.append(f"Step {step_num} (file_reader): Error - {str(e)}")
    
    elif "[final_answer]" in current_line:
        # Skip final_answer in executor, answer_node will handle it
        pass
    
    else:
        new_results.append(f"Step {step_num}: Unknown step type - {current_line}")
    
    return {"tool_results": new_results, "current_step": step_num}

def answer_node(state: AgentState):
    """Produce final answer based on tool results and original question."""
    question = state["messages"][-1]["content"]
    results = "\n".join(state.get("tool_results", []))
    
    prompt = f"""Answer the user's question using the information below.
Question: {question}
Tool results:
{results}

Provide a clear, accurate answer based on the file data and other results.
If file was read, summarize the relevant information.
If unsure, say 'I could not find the answer'."""
    
    final = llm.invoke(prompt).content
    return {"final_answer": final}