from fastmcp import FastMCP

math_mcp = FastMCP(name="math_server")


@math_mcp.tool()
def add(a: int, b: int) -> int:
    """
    Adds two numbers together.

    Args:
        a (int): The first number to add.
        b (int): The second number to add.

    Returns:
        int: The sum of a and b.
    """
    return a + b


@math_mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply two numbers together.

    Args:
        a (int): The first number to add.
        b (int): The second number to add.

    Returns:
        int: The product of a and b.
    """
    return a * b
