from fastmcp import FastMCP
from sub_servers.math_server import math_mcp
from sub_servers.graphviz_server import graphviz_mcp
from sub_servers.manim_server import manim_mcp
import asyncio


main_mcp = FastMCP(
    name="MainServer",
    host="127.0.0.1",
    port="8000",
    on_duplicate_tools="error",  # error on duplicate tools
)


# Import subserver
async def setup():
    await main_mcp.import_server("sub_server", math_mcp)
    await main_mcp.import_server("graphviz_server", graphviz_mcp)
    await main_mcp.import_server("manim_server", manim_mcp)


if __name__ == "__main__":
    asyncio.run(setup())
    main_mcp.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
