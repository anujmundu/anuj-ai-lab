import requests
from app.core.config import settings


class OllamaService:

    def generate(
        self,
        prompt: str,
        model: str | None = None
    ):

        payload = {
            "model": model or settings.DEFAULT_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }

        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=300
        )

        response.raise_for_status()

        return response.json()["response"]


ollama_service = OllamaService()