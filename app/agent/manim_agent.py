from pathlib import Path
from app.agent import Agent
from smolagents import CodeAgent


class ManimAgent(Agent):
    def __init__(self):
        """
        Initializes the ManimAgent and calls the base Agent initializer.

        """
        super().__init__()

    def setup_agent(self) -> None:
        """
        Sets up the CodeAgent with the current tools and model.
        """
        self.agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            additional_authorized_imports=[
                "manim.*",
                "manim.mobject",
                "manim.animation",
                "numpy",
            ],
        )

    def __call__(
        self, pdf: bytes | str | list[bytes] | list[str] | None, prompt: str
    ) -> str:
        """
        Call Manim Agent
        Args:
            pdf: The uploaded PDF file(s).
            prompt: The user message.

        Returns:
            str: Path to the generated video file.
        """
        self.agent.run(task=prompt)

        # TODO implement agent logic
        app_dir = (
            Path(__file__).parent.parent.parent / "videos/test.mp4"
        )  # returns a mp4 path form /videos
        return str(app_dir)
