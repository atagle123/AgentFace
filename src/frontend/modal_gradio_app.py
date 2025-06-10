import modal
from ..backend.summary_agent import PDF_SummarizerAgent
from ..backend.manim_agent import Manim_Agent
from ..app import app 
#ui_app = modal.App("gradio_app")

gradio_app_image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "fastapi[standard]==0.115.4",
    "pydantic==2.9.2",
    "starlette==0.41.2",
    "gradio==4.44.1",
    "gradio-pdf==0.0.15",
)


@app.function(
    image=gradio_app_image,
    # gradio requires sticky sessions
    # so we limit the number of concurrent containers to 1
    # and allow it to scale to 1000 concurrent inputs
    max_containers=1,
)
@modal.concurrent(max_inputs=1000)
@modal.asgi_app()
def gradio_ui():
    import uuid
    import gradio as gr
    from fastapi import FastAPI
    from gradio.routes import mount_gradio_app
    from gradio_pdf import PDF


    def pdf_path_to_bytes(path: str):
        # Read the original PDF
        with open(path, "rb") as f:
            pdf_bytes = f.read()

        return (pdf_bytes)


    def upload_pdf(pdf_file):

        pdf_bytes = pdf_path_to_bytes(pdf_file) # TODO manage errors
        return pdf_bytes

    def generate_video(pdf_bytes, prompt: str, session_id: str):
        if not isinstance(prompt, str):
            prompt = ""

        if session_id == "" or session_id is None: # TODO use session id to video 
            session_id = str(uuid.uuid4())

        summary = PDF_SummarizerAgent().summarize_pdf.remote(pdf_bytes, prompt = prompt)
        print(summary)
        video_path = Manim_Agent().generate_manim.remote(topic = summary.get("topic"), context = summary.get("context"))
        
        return video_path

    with gr.Blocks(theme="soft") as demo:
        session_id = gr.State("")
        pdf_bytes_state = gr.State(None)
        gr.Markdown("# Chat with PDF")
        with gr.Row():
            with gr.Column(scale=1):
                chatbox = gr.Textbox(label="Prompt", placeholder="Describe the animation you want...")
                submit = gr.Button("Generate Video", variant="primary") # TODO make submit when summary is ready... important, change interface submit does it all
            with gr.Column(scale=1):
                pdf = PDF(label="Upload a PDF", interactive=True) # gradio checks that the file is a pdf
                pdf.upload(upload_pdf, [pdf], [pdf_bytes_state])
        video_output = gr.Video(label="Generated Video")
        submit.click(
            fn=generate_video,
            inputs=[pdf_bytes_state, chatbox, session_id],
            outputs=video_output,
        )

    return mount_gradio_app(app=FastAPI(), blocks=demo, path="/")