import gradio as gr
import base64

def leer_pdf_y_generar_url(file):
    
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

    <script>
        document.addEventListener("mouseup", () => {{
            const selectedText = window.getSelection().toString();
            if (selectedText.length > 0) {{
                const textarea = document.querySelector('textarea[aria-label="🧠 Texto seleccionado"]');
                if (textarea) {{
                    textarea.value = selectedText;
                    textarea.dispatchEvent(new Event('input'));  // <- notifica a Gradio que cambió
                }}
            }}
        }});
    </script>
    """
    return html

with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align: center;'>📄 Amazing PDF</h1>")

    archivo_pdf = gr.File(label="Sube tu PDF", file_types=[".pdf"])
    resultado_html = gr.HTML()
    texto_seleccionado = gr.Textbox(label="🧠 Texto seleccionado", lines=4)
    
    archivo_pdf.change(fn=leer_pdf_y_generar_url, inputs=archivo_pdf, outputs=resultado_html)

demo.launch()