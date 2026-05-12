from langchain_core.tools import tool 
from bs4 import BeautifulSoup
import requests
import re
@tool 
def web_scraper_tool(url:str) ->str:
    """Scrape content from the Url. To be used when information/content of full page from a website"""
    try:
       response=requests.get(url,timeout=10)
       response.raise_for_status()

       soup = BeautifulSoup(response.content,'lxml')
       for script in soup(['script','style']):
           script.decompose()
       main_content = (soup.find("main") or soup.find("article") or 
                       soup.find("div",class_=re.compile(r"content|body")) or soup.body )
       text = main_content.get_text(separator="\n",strip=True) # pyright: ignore[reportOptionalMemberAccess]
       lines = [line.strip() for line in text.split("\n") if line.strip()]
       return "\n".join(lines[:50])             
    except Exception as e:
        return f"Error: {str(e)}"
    
