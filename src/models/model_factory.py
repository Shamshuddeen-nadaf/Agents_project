from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
MODEL_NAME = "qwen2:7b"
def get_llm(use_local=True):
  if use_local:
    return ChatOllama(model=MODEL_NAME, temperature=0)
  else:
    print("We don't have an API yet youre getting local regardless")
    return ChatOllama(model=MODEL_NAME,temperature=0)
  

if __name__ == "__main__":
  model = get_llm()
  print(model.invoke(
    [SystemMessage("You are cheese assistant, reply everything with cheese analogies"),
     HumanMessage("What is the half of four hundred and twenty two")]
  ).content
  )
  