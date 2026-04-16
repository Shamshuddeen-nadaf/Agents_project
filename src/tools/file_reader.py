from langchain_core.tools import tool
import pandas as pd
from langchain_pymupdf4llm import PyMuPDF4LLMLoader 
from pathlib import Path
def _read_pdf(file_path:str)->str:
  loader = PyMuPDF4LLMLoader(
    file_path=file_path,
    mode='single',
    pages_delimiter="<--!PAGE DELIMITER!-->"
  )
  docs = loader.load()
  return docs[0].page_content

def _read_csv(file_path:str)->str:
  dataFrame = pd.read_csv(file_path)
  text = dataFrame.to_string()
  return text

def _read_text(file_path:str)->str:
  with open(file_path,'r') as textFile:
    return textFile.read()


@tool 
def file_reader(file_path:str)->str:
  ''' Tool to read a single file. Only has capabilites to read txt,csv and pdf.
      The file is read and converted into string, yes the entire file is converted into string'''
  pathObj = Path(file_path)
  suffix = pathObj.suffix
  try:
    if suffix == ".pdf":
      return _read_pdf(file_path=file_path)
    elif suffix == ".csv":
      return _read_csv(file_path=file_path)
    elif suffix == ".txt":
      return _read_text(file_path=file_path)
    else:
      return "File reading failed either the given path doesnt have an extension or some error happend "
  except Exception as e:
    print(f"OOPS : {e}")
    return f"SOME ERROR HAS OCCURED {e}"


if __name__ == '__main__':
  print(file_reader.invoke(r"C:\Users\Shamshuddeen\Documents\Agents_project\src\FILES\jew.txt"))