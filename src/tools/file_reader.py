from langchain_core.tools import tool
import pandas as pd
import pymupdf
from pathlib import Path


def _read_pdf(file_path: str) -> str:
    doc = pymupdf.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text


def _read_csv(file_path: str) -> str:
    dataFrame = pd.read_csv(file_path)
    text = dataFrame.to_string()
    return text


def _read_text(file_path: str) -> str:
    with open(file_path, 'r') as textFile:
        return textFile.read()


@tool
def file_reader(file_path: str) -> str:
    """Tool to read a single file. Only has capabilities to read txt, csv and pdf."""
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
            return "File reading failed: invalid or missing extension"
    except Exception as e:
        return f"Error: {e}"


if __name__ == '__main__':
    print(file_reader.invoke(r"test.txt"))