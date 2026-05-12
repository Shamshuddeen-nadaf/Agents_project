'''
Defines the structure for state of the Agent.  
There are many types of classes after asking claude I've added them.
Hopefully they will make the agent less dumb.
'''
from typing_extensions import TypedDict,Any,Literal 
from typing import Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
import operator
from datetime import datetime
class ReasoningTrace(TypedDict):
    '''Trace of the Reasoning inside the Agent'''
    step:int
    thought:str # thinking of the Agent
    confidence:float # self assesed confidence for the strategy
    strategy:str # "decompose" "backtrack" etc.
    timestamp:str # time 
class ActionRecord(TypedDict):
    '''Records the actions taken by the agent'''
    step:int
    tool_name:str
    tool_input:dict[str,Any]
    raw_output:str
    parsed_output:Any
    success:bool
    error_message:Optional[str]
    timestamp:str
class PlanStep(TypedDict):
    '''Planning utility class'''
    id:str # step1 , step etc.
    description:str
    depends_on:list[str] #id's of the required steps to be ran first
    status:Literal["pending", "running", "done", "failed", "skipped"]
    result:Optional[str]
class MemoryEntry(TypedDict):
    '''For the memory required'''
    key:str
    value:Any # to store user instructions, any information relevant or needed for future use.
    source:str # step that generated said information
    confidence:float
    created_at:str
class SelfCritique(TypedDict):
    '''Class to track self critique'''
    step:int
    critique:str
    severity:Literal["low","medium","high"]
    action_taken:str
class HypothesisEntry(TypedDict):
    id: str
    hypothesis: str
    evidence_for: list[str]
    evidence_against: list[str]
    status: Literal["active", "confirmed", "rejected"]
class AgentState(TypedDict):
    #core 
    messages:Annotated[list[BaseMessage],operator.add]
    iteration:int
    max_iterations:int
    task:str
    status:Literal["planning", "executing", "reflecting",
        "replanning", "verifying", "done", "failed"]
    #Resoning and congnition
    reasoning_trace: Annotated[list[ReasoningTrace], operator.add]
    current_strategy: str               # e.g. "divide-and-conquer", "hypothesis-testing"
    confidence_score: float             # rolling estimate of overall progress
    uncertainty_flags: list[str]        # things the agent knows it doesn't know
    #Planning
    plan: list[PlanStep]                # structured execution plan
    current_step_id: str                # which plan step is active
    replan_count: int                   # how many times the plan was revised
    replan_reasons: Annotated[list[str], operator.add]
    #Action and Tool use
    action_history: Annotated[list[ActionRecord], operator.add]
    failed_tools: Annotated[list[str], operator.add]  # tools that errored
    #Memory
    working_memory: dict[str, Any]      # fast scratch space (overwritten freely)
    episodic_memory: Annotated[list[MemoryEntry], operator.add]  # durable facts
    entity_map: dict[str, Any]          # named entities discovered: {name: attributes}
    #Hypothesis and Verification
    hypotheses: list[HypothesisEntry]   # active theories being tested
    verified_facts: Annotated[list[str], operator.add]
    contradictions: Annotated[list[str], operator.add]
    #Self Correction
    critiques: Annotated[list[SelfCritique], operator.add]
    retry_count: int                    # retries on current step
    max_retries_per_step: int
    backtrack_to_step: Optional[str]    # set when agent decides to backtrack
    #Context and Grounding
    retrieved_documents: list[dict]     # RAG results, keyed by query
    external_context: dict[str, Any]    # injected by caller (user profile, env vars)
    constraints: list[str]             # rules the agent must respect
    time_budget_ms: Optional[int]       # optional deadline

    #  Output
    intermediate_answers: Annotated[list[str], operator.add]  # partial results
    final_answer: Optional[str]
    answer_confidence: float
    citations: list[str]               # sources used
    error: Optional[str]

if __name__ == "__main__":
    print("state is running ...\n No errors :)")