import gradio as gr
from smolagents import ToolCollection
from app.agent import Agent, ManimAgent
import base64

def leer_pdf(file):
    
    if file is None:
        return "<p>No se subió ningún archivo.</p>"

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
    with gr.Blocks() as demo:
        gr.Markdown("<h1 style='text-align: center;'>📄 Amazing PDF</h1>")

        pdf = gr.File(label="Upload PDF", file_types=[".pdf"])
        resultado_html = gr.HTML()
        
        pdf.change(fn=leer_pdf, inputs=pdf, outputs=resultado_html)

        with gr.Row():
            chatbox = gr.Textbox(label="Prompt")

        with gr.Row():
            generateSummary = gr.Button("Generate Summary")
            generateVideo = gr.Button("Generate Video")
            generateDiagram = gr.Button("Generate Diagram")

        video_output = gr.Video(label="Result Video")

        generateSummary.click(
            fn=trigger_fn,
            inputs=[pdf, chatbox],
            outputs=video_output,
        )

        generateVideo.click(
            fn=trigger_fn,
            inputs=[pdf, chatbox],
            outputs=video_output,
        )

        generateDiagram.click(
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
