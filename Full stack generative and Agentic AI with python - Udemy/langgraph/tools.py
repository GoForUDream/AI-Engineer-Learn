from langchain_core.tools import tool


@tool
def calculator(expression: str):
    """Execute a mathematical expression and return the result."""

    return str(eval(expression))
