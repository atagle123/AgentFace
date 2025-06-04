from smolagents import InferenceClientModel, TransformersModel, CodeAgent, LiteLLMModel
from dotenv import load_dotenv
import os

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class Agent:
    def __init__(self, model_id: str = "Qwen/Qwen2.5-Coder-32B-Instruct"):
        """
        Initializes the Agent with a model.

        Args:
            model_id (str): The model identifier to use.
        """
        # self.model = TransformersModel(
        #     model_id=model_id,
        #      device="cuda",
        #      max_new_tokens=5000,
        #  )
        
        self.model = LiteLLMModel(
            model_id="openai/deepseek-r1-distill-llama-70b",
            api_base="https://api.groq.com/openai/v1",
            api_key=str(GROQ_API_KEY)
        )
        self.model.flatten_messages_as_text = True
        
        # self.model = InferenceClientModel(
        #     model_id=model_id,
        #     token=str(HF_TOKEN),
        # )
        
        self.tools = []

    def add_tools(self, tools: list) -> None:
        """
        Adds tools to the agent.

        Args:
            tools (list): A list of smolagents tools to add.
        """
        self.tools += tools

    def setup_agent(self) -> None:
        """
        Sets up the CodeAgent with the current tools and model.
        """
        self.agent = CodeAgent(tools=self.tools, model=self.model, additional_authorized_imports=["manim.*", "manim.mobject", "manim.animation", "numpy"])

    def __call__(self, prompt: str):
        """
        Runs the agent on the given prompt.

        Args:
            prompt (str): The prompt or task to run.

        """
        self.agent.run(task=prompt)


def main():
    agent = Agent()
    agent.setup_agent()
    prompt = "hola que tal"
    agent(prompt)


if __name__ == "__main__":
    main()
