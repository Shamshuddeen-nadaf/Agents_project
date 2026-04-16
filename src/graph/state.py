from typing import List,Optional,Annotated,TypedDict
import operator 

class AgentState(TypedDict):
  messages:Annotated[List[dict],operator.add] #list of messages with a concatenation i.e. operator.add
  plan:Optional[str] # the plan the agent is executing
  current_step:Optional[int] #number of step the agent is currently on
  tool_results:Annotated[List[str],operator.add] #list of tool results with a concatenation i.e. operator.add
  final_answer:Optional[str] #the final answer of the agent
  