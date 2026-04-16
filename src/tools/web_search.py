from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

@tool 
def web_search(query:str)->str:
  """Search the web for current information. Use this for facts, news, or data not in your memory."""
  return DuckDuckGoSearchRun().run(query)
