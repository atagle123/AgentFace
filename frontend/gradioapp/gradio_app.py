import gradio as gr
from smolagents import ToolCollection
from app.agent import Agent, ManimAgent
import base64

def read_pdf(file):
    
    if file is None:
        return "<p>No file uploaded.</p>"

    # Convertimos el PDF a base64
    with open(file.name, "rb") as f:
        b64_pdf = base64.b64encode(f.read()).decode("utf-8")

    # HTML con iframe que muestra el PDF desde base64
    html = f"""
    <iframe id="pdf-viewer" src="data:application/pdf;base64,{b64_pdf}"
            width="100%" height="600px"
            style="border: 1px solid #ccc;"></iframe>
    """
    return html


def create_manim_demo(trigger_fn: callable) -> gr.Blocks:
    """
    Creates and returns the Gradio Blocks demo.

    Args:
        trigger_fn (Callable): Function to call when the button is clicked.

    Returns:
        gr.Blocks: The Gradio app.
    """
    def process_with_preview(pdf_file, prompt):
        """Process the request and show PDF preview if needed."""
        if pdf_file is not None:
            # Generate video
            video_path = trigger_fn(pdf_file, prompt)
            return video_path
        return None

    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=1):
                pdf = gr.File(label="Upload PDF", file_types=[".pdf"])
                chatbox = gr.Textbox(label="Prompt", placeholder="Describe the animation you want...")
                submit = gr.Button("Generate Video", variant="primary")

            with gr.Column(scale=1):
                pdf_preview = gr.HTML(label="PDF Preview")

        video_output = gr.Video(label="Generated Video")

        # Show PDF preview when file is uploaded
        pdf.change(
            fn=lambda file: read_pdf(file) if file else "<p>No PDF uploaded</p>",
            inputs=pdf,
            outputs=pdf_preview
        )

        # Generate video when button is clicked
        submit.click(
            fn=process_with_preview,
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
