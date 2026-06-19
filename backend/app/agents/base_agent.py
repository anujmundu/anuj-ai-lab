from app.services.ollama_service import ollama_service


class BaseAgent:

    def __init__(
        self,
        model: str = "qwen2.5:1.5b"
    ):
        self.model = model

    def run(
        self,
        prompt: str
    ):

        return ollama_service.generate(
            prompt=prompt,
            model=self.model
        )