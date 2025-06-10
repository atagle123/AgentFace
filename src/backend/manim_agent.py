import modal
import asyncio
from .utils import Ollama_server
import time
from ..app import app


#manim_app = modal.App("Manim_agent")

cache_bust = str(int(time.time()))  # or use a commit hash, etc.


manim_agent_image = modal.Image.from_registry("python:3.12-slim" # TODO: build image step by step and reuse images to other servers... 
    ).apt_install(
        "curl",
        "git",
        "portaudio19-dev",
        "libsdl-pango-dev",
        "wget",
        "texlive-full","build-essential" ,"python3-dev" ,"libcairo2-dev" ,"libpango1.0-dev",
    ).env({
        "CACHE_BUST": cache_bust, } # 👈 this forces all following steps to rerun
    ).run_commands( 
        "curl -fsSL https://ollama.com/install.sh | sh", # ollama
        "git clone https://github.com/atagle123/TheoremExplainAgent",
        "mkdir -p TheoremExplainAgent/models",
        "mkdir -p TheoremExplainAgent/output",
        "wget -P TheoremExplainAgent/models https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v0_19.onnx",
        "wget -P TheoremExplainAgent/models https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices.bin",
        "pip install -r TheoremExplainAgent/requirements.txt",
    ).workdir("/TheoremExplainAgent",
    ).env({
        # Set .env-style variables using Modal secrets
        "KOKORO_MODEL_PATH": "TheoremExplainAgent/models/kokoro-v0_19.onnx",
        "KOKORO_VOICES_PATH": "TheoremExplainAgent/models/voices.bin",
        "KOKORO_DEFAULT_VOICE": "af",
        "KOKORO_DEFAULT_SPEED": "1.0",
        "KOKORO_DEFAULT_LANG": "en-us",
        })


@app.cls(image=manim_agent_image, gpu="A10G")
class Manim_Agent:

    @modal.enter()
    def init_ollama(self):
        import os
        os.environ["PYTHONPATH"] = f"{os.getcwd()}:{os.environ.get('PYTHONPATH', '')}"
        self.model = "devstral:24b"

        ollama_server = Ollama_server()
        ollama_server.pull_model(self.model)


    @modal.method()
    def generate_manim(self, topic: str, context: str):
        from mllm_tools.litellm import LiteLLMWrapper
        from generate_video import VideoGenerator
        from src.config.config import ConfigDefaults

        DEFAULTS = ConfigDefaults()

        DEFAULTS.model = f"ollama/{self.model}"
        DEFAULTS.helper_model = f"ollama/{self.model}"

        planner_model = LiteLLMWrapper(
            model_name=DEFAULTS.model,
            temperature=0.7,
            print_cost=True,
            verbose=DEFAULTS.verbose,
            use_langfuse=DEFAULTS.use_langfuse
        )

        helper_model = LiteLLMWrapper(
            model_name=DEFAULTS.helper_model if DEFAULTS.helper_model else DEFAULTS.model,
            temperature=0.7,
            print_cost=True,
            verbose=DEFAULTS.verbose,
            use_langfuse=DEFAULTS.use_langfuse
        )

        scene_model = LiteLLMWrapper(
            model_name=DEFAULTS.model,
            temperature=0.7,
            print_cost=True,
            verbose=DEFAULTS.verbose,
            use_langfuse=DEFAULTS.use_langfuse
        )

        video_generator = VideoGenerator(
            planner_model=planner_model,
            scene_model=scene_model,
            helper_model=helper_model,
            output_dir=DEFAULTS.output_dir,
            verbose=DEFAULTS.verbose,
            use_rag=DEFAULTS.use_rag,
            use_context_learning=DEFAULTS.use_context_learning,
            context_learning_path=DEFAULTS.context_learning_path,
            chroma_db_path=DEFAULTS.chroma_db_path,
            manim_docs_path=DEFAULTS.manim_docs_path,
            embedding_model=DEFAULTS.embedding_model,
            use_visual_fix_code=DEFAULTS.use_visual_fix_code,
            use_langfuse=DEFAULTS.use_langfuse,
            max_scene_concurrency=DEFAULTS.max_scene_concurrency
        )

        if DEFAULTS.only_gen_vid:
            video_generator.render_video_fix_code(topic, context, max_retries=DEFAULTS.max_retries)
            return {"status": "rendered only"}

        if DEFAULTS.only_combine:
            video_generator.combine_videos(topic)
            return {"status": "combined only"}

        asyncio.run(video_generator.generate_video_pipeline(
            topic,
            context,
            max_retries=DEFAULTS.max_retries,
            only_plan=DEFAULTS.only_plan,
            only_render=DEFAULTS.only_render,
        ))

        if not DEFAULTS.only_plan and not DEFAULTS.only_render:
            video_generator.combine_videos(topic)
        video_path = "asd" # TODO placeholder for video path replace with real video, utilize a modal mount with session id to store the videos...
        return video_path

    @modal.exit()
    def exit_function(self):
        pass
    

#@manim_app.local_entrypoint()
#def main():
#    Manim_Agent().generate_manim.remote()

