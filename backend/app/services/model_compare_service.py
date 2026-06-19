import time

from app.services.ollama_service import ollama_service


class ModelCompareService:

    MODELS = [
        "qwen2.5:1.5b",
        "gemma2:9b"
    ]

    def compare_models(
        self,
        prompt: str
    ):

        results = {}

        for model in self.MODELS:

            start = time.time()

            output = ollama_service.generate(
                prompt=prompt,
                model=model
            )

            latency = round(
                time.time() - start,
                2
            )

            results[model] = {
                "latency_seconds": latency,
                "response": output
            }

        return results


model_compare_service = ModelCompareService()