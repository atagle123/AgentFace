import modal
from pathlib import Path

MINUTES = 60  # seconds
PDF_ROOT = Path("/vol/pdfs/")

app = modal.App("pdf-to-manim")

web_image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi[standard]==0.115.4",
    "pydantic==2.9.2",
    "starlette==0.41.2",
    "gradio==4.44.1",
    "gradio-pdf==0.0.15",
    "fitz"
)


@app.function(
    image=web_image,
    # gradio requires sticky sessions
    # so we limit the number of concurrent containers to 1
    # and allow it to scale to 1000 concurrent inputs
    max_containers=1,
)
@modal.concurrent(max_inputs=1000)
@modal.asgi_app()
def ui():
    import uuid

    import gradio as gr
    from fastapi import FastAPI
    from gradio.routes import mount_gradio_app
    from gradio_pdf import PDF
    import fitz

    web_app = FastAPI()


    def upload_pdf(pdf_path, prompt: str, session_id):
        if session_id == "" or session_id is None:
            # Generate session id if new client
            session_id = str(uuid.uuid4())

        # TODO pdf pipeline 
        #session_dir = PDF_ROOT / f"{session_id}"
        #session_dir.mkdir(exist_ok=True, parents=True)
        #doc = fitz.open(session_dir)
        #doc.save(output_pdf)
        #doc.close()
        return session_id

    def process_with_preview(pdf_file, prompt: str):
        """Process the request and show PDF preview if needed."""
        if pdf_file is not None:
            # Generate video
            #video_path = trigger_fn(pdf_file, prompt)
            return "video_path" # Placeholder for video path
        return None

    with gr.Blocks(theme="soft") as demo:
        session_id = gr.State("")

        gr.Markdown("# Chat with PDF")
        with gr.Row():
            with gr.Column(scale=1):
                chatbox = gr.Textbox(label="Prompt", placeholder="Describe the animation you want...")
                submit = gr.Button("Generate Video", variant="primary")

            with gr.Column(scale=1):
                pdf = PDF(
                    label="Upload a PDF",
                    interactive=True
                )
                pdf.upload(upload_pdf, [pdf, session_id], session_id)

        video_output = gr.Video(label="Generated Video")

        submit.click(
            fn=process_with_preview,
            inputs=[pdf, chatbox],
            outputs=video_output,
        )

    return mount_gradio_app(app=web_app, blocks=demo, path="/")