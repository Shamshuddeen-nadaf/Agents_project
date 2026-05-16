import subprocess
import sys
import tempfile
from pathlib import Path
from langchain_core.tools import tool

@tool
def python_sandbox_tool(code:str)->str:
  '''Runs python code in an isolated subprocess'''
  with tempfile.TemporaryDirectory() as tmpdir:
    filePath = Path(tmpdir) / "script.py"
    filePath.write_text(code)
    result = subprocess.run(
        [sys.executable,str(filePath)],
        capture_output=True,
        text=True,
        timeout=60
    )
    return result.stdout if result.returncode == 0 else result.stderr