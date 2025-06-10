import subprocess
import time


class Ollama_server:
    def __init__(self):
        print("Starting Ollama server...")
        subprocess.Popen(["ollama", "serve"])
        
        # Wait for server to start
        time.sleep(10)
    
    def pull_model(self, model:str = "devstral:24b"):
        print("Downloading model...")
        subprocess.run(["ollama", "pull", model])
        
        print("Ollama server ready!")