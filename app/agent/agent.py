from smolagents import InferenceClientModel, TransformersModel, CodeAgent, LiteLLMModel
from dotenv import load_dotenv
import os
from abc import ABC, abstractmethod

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


class Agent(ABC):
    """
    Abstract base class for agents.
    """

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
        # self.model = InferenceClientModel(
        #    model_id=model_id,
        #    token=str(HF_TOKEN),
        # )

        self.model = LiteLLMModel(
            model_id="openai/deepseek-r1-distill-llama-70b",
            api_base="https://api.groq.com/openai/v1",
            api_key=str(GROQ_API_KEY),
        )
        self.model.flatten_messages_as_text = True

        self.tools: list = []

    def add_tools(self, tools: list) -> None:
        """
        Adds tools to the agent.

        Args:
            tools (list[Any]): A list of smolagents tools to add.
        """
        self.tools += tools

    @abstractmethod
    def setup_agent(self) -> None:
        """
        Sets up the CodeAgent with the current tools and model.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def __call__(self, prompt: str):
        """
        Runs the agent on the given prompt.
        Must be implemented by subclasses.

        Args:
            prompt (str): The prompt or task to run.

        Returns:
            Any: The result of the agent's execution.
        """
        pass


class ExampleChatAgent(Agent):
    """
    Example Agent to chat
    """

    def setup_agent(self) -> None:
        self.agent = CodeAgent(tools=self.tools, model=self.model)

    def __call__(self, prompt: str):

        return self.agent.run(task=prompt)


def main():
    agent = ExampleChatAgent()
    agent.setup_agent()
    prompt = "hola que tal"
    agent(prompt)


if __name__ == "__main__":
    main()
