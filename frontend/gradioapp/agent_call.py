from smolagents import ToolCollection
from app.agent import Agent


def main(prompt):
    with ToolCollection.from_mcp(
        {"url": "http://127.0.0.1:8000/mcp", "transport": "streamable-http"},
        trust_remote_code=True,
    ) as tool_collection:
        agent = Agent()
        agent.add_tools([*tool_collection.tools])
        agent.setup_agent()
        agent(prompt)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run the agent with tools from MCP server.")
    parser.add_argument("--prompt", type=str, default="sum me two numbers 123 and 234")
    args = parser.parse_args()
    main(args.prompt)
