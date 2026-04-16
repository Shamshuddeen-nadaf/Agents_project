import re
import math
from langchain_core.tools import tool

def _calculate(expression: str) -> str:
    """Evaluate a math expression like '2+2' or 'sqrt(16)'. Returns the result as a string."""
    allowed_functions = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
        "sqrt": math.sqrt
    }

    # Allowed: digits, whitespace, + - * / ( ) . , and the function names above
    pattern = r'^(?:[\d\s\+\-\*\/\(\)\.\,]|abs|round|min|max|pow|sqrt)+$'

    if not re.match(pattern, expression):
        return "Error: Invalid characters in expression"

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_functions)
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"

@tool
def calculator(expression: str) -> str:
    """LangChain tool wrapper for basic math evaluation."""
    return _calculate(expression)

if __name__ == "__main__":
    test_expressions = [
        ("2+2", "4"),
        ("sqrt(16)", "4.0"),
        ("(5+3)*2", "16"),
        ("abs(-5)", "5"),
        ("pow(2,3)", "8"),
        ("x+2", "Error: Invalid characters"),
        ("sqrt(-1)", "Calculation error:"),
    ]

    print("Testing calculator...")
    for expr, expected in test_expressions:
        result = _calculate(expr)
        status = "YES" if expected in result else "NO"
        print(f"{status} {expr!r:20} : {result}")