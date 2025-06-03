from smolagents import ToolCollection
from app.agent import Agent


def main():
    with ToolCollection.from_mcp(
        {"url": "http://127.0.0.1:8000/mcp", "transport": "streamable-http"},
        trust_remote_code=True,
    ) as tool_collection:
        agent = Agent()
        agent.add_tools([*tool_collection.tools])
        agent.setup_agent()
        prompt = "sum me two numbers 123 and 234"
        agent(prompt)


if __name__ == "__main__":
    main()
