from langchain_core.tools import tool
import pandas as pd
import pymupdf
from pathlib import Path
import json

ALLOWED_EXTENSIONS: set[str] = {".pdf",".csv",".txt",".json",".md"}

def _is_allowed_extension(suffix:str)->bool:
    return suffix.lower() in ALLOWED_EXTENSIONS

def _read_pdf(file_path: str) -> str:
    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n" # type: ignore
    return text


def _read_csv(file_path: str) -> str:
    dataFrame = pd.read_csv(file_path)
    text = dataFrame.to_string()
    return text

def _read_json(file_path:str)->str:
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    text = json.dumps(data,indent=2)
    return text
 
def _read_text(file_path: str) -> str:
    with open(file_path, 'r') as textFile:
        return textFile.read()


@tool
def file_reader(file_path: str) -> str:
    """Tool to read a single file. Only has capabilities to read txt,csv,pdf,json and md."""
    pathObj = Path(file_path)
    suffix = pathObj.suffix
    if not suffix:
        return "File reading failed: No File extension found"
    if not _is_allowed_extension(suffix):
        return f"Unsupported file type {suffix},try: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
    try:
        if suffix == ".pdf":
            return _read_pdf(file_path=file_path)
        elif suffix == ".csv":
            return _read_csv(file_path=file_path)
        elif suffix in  {".txt",".md"}:
            return _read_text(file_path=file_path)
        elif suffix == '.json':
            return _read_json(file_path=file_path)
        else:
            return "File reading failed: it was in allowed list but still not in the one huh weird this should'nt be happening"
    except Exception as e:
        return f"Error: {e}"
