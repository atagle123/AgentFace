import modal
from .utils import Ollama_server
from ..app import app

#pdf_app = modal.App("pdf_app")


pdf_summarizer_image = (
    modal.Image.debian_slim()
    .apt_install("curl", "poppler-utils")  # poppler for PDF processing
    .run_commands("curl -fsSL https://ollama.com/install.sh | sh")
    .pip_install(
        "llama-index",
        "llama-index-embeddings-ollama", 
        "llama-index-llms-ollama",
        "requests",
        "PyPDF2",
        "pdf2image",
        "sentence-transformers"
    )
)

@app.cls(
    image=pdf_summarizer_image,
    gpu="A10G",
    timeout=15000, #  volumes={"/pdftmp": modal.Volume.from_name("pdf-cache", create_if_missing=True)}
)
class PDF_SummarizerAgent:
    
    @modal.enter()
    def init_ollama(self):
         # Start Ollama server
        ollama_server = Ollama_server()
        ollama_server.pull_model(model = "llama3.2:3b")
        ollama_server.pull_model(model = "nomic-embed-text")
        
        print("Setting up LlamaIndex...")
        
        # Import LlamaIndex components
        from llama_index.core import Settings
        from llama_index.embeddings.ollama import OllamaEmbedding
        from llama_index.llms.ollama import Ollama
        from llama_index.core.node_parser import SemanticSplitterNodeParser
        from llama_index.core.extractors import SummaryExtractor
        from llama_index.core.ingestion import IngestionPipeline
        
        # Setup Ollama LLM and embeddings
        self.llm = Ollama(
            model="llama3.2:3b",
            base_url="http://localhost:11434",
            temperature=0.1,
            request_timeout=120.0
        )
        
        self.embed_model = OllamaEmbedding(
            model_name="nomic-embed-text",
            base_url="http://localhost:11434",
            request_timeout=120.0
        )
        
        # Configure global settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

                # Setup semantic splitter
        self.splitter = SemanticSplitterNodeParser(
            buffer_size=6,
            breakpoint_percentile_threshold=95,
            embed_model=self.embed_model,
        )
        
        # Create ingestion pipeline with semantic splitting
        self.pipeline = IngestionPipeline(
            transformations=[
                self.splitter,
                SummaryExtractor(llm=self.llm, summaries=["prev", "self", "next"])
            ]
        )

    @modal.method()
    def summarize_pdf(self, pdf_bytes: bytes, prompt:str, chunk_size: int = 1024, overlap: int = 200):
        """
        Summarize a PDF using LlamaIndex semantic splitting and Ollama
        """
        # Import LlamaIndex components
        from llama_index.core import Document, VectorStoreIndex
        import PyPDF2
        from io import BytesIO
        
        
        # Extract text from PDF
        print("Extracting text from PDF...")
        pdf_file = BytesIO(pdf_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        if not text.strip():
            return {"error": "Could not extract text from PDF"} # TODO manage errors
        
        print(f"Extracted {len(text)} characters from PDF")
        
        # Create document
        document = Document(text=text)
        
        print("Processing document with semantic splitting...")
        nodes = self.pipeline.run(documents=[document])
        
        print(f"Created {len(nodes)} semantic chunks")
        
        # Create vector index
        print("Creating vector index...")
        index = VectorStoreIndex(nodes)
        
        # Create query engine
        query_engine = index.as_query_engine(
            similarity_top_k=5,
            response_mode="tree_summarize"
        )
        
        # Generate summary
        print("Generating summary...")
        summary_query = f"""
        Now you are an expert teacher like lecunn, hinton or feynmann, and you need to summarize the paper with the most relevant formulas and insights.
        Pay attention to the prompt: {prompt}
        """
        
        summary_response = query_engine.query(summary_query)
        
        # Generate key insights
        print("Generating key insights...")
        topic_query = """
        Which is the main topic of this paper, only return one phrase. 
        """
        
        topic_response = query_engine.query(topic_query) # TODO make this efficient
        
        return {
            "topic": str(topic_response),
            "context": str(summary_response)
            }
    
    @modal.exit()
    def exit(self):
        pass