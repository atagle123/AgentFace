import gradio as gr
from smolagents import ToolCollection
from app.agent import Agent, ManimAgent


def create_manim_demo(trigger_fn: callable) -> gr.Blocks:
    """
    Creates and returns the Gradio Blocks demo.

    Args:
        trigger_fn (Callable): Function to call when the button is clicked.

    Returns:
        gr.Blocks: The Gradio app.
    """
    with gr.Blocks() as demo:
        with gr.Row():
            pdf = gr.File(label="Upload PDF", file_types=[".pdf"])
            chatbox = gr.Textbox(label="Prompt")
            submit = gr.Button("Generate Video")

        video_output = gr.Video(label="Result Video")

        submit.click(
            fn=trigger_fn,
            inputs=[pdf, chatbox],
            outputs=video_output,
        )
    return demo


def setup_agent_with_tools() -> Agent:
    """
    Initializes the ManimAgent and adds tools from the MCP server.

    Returns:
        ManimAgent: The configured  manim agent.
    """
    with ToolCollection.from_mcp(
        {"url": "http://127.0.0.1:8000/mcp", "transport": "streamable-http"},
        trust_remote_code=True,
    ) as tool_collection:
        agent = ManimAgent()
        agent.add_tools([*tool_collection.tools])
    agent.setup_agent()
    return agent


def main() -> None:
    """
    Main entry point for launching the Gradio app.
    """
    agent = setup_agent_with_tools()
    demo = create_manim_demo(trigger_fn=lambda pdf, msg: agent(pdf, msg))
    demo.launch()


if __name__ == "__main__":
    main()
