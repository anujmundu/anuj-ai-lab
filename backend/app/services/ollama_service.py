import time

import requests

from app.core.config import settings
from app.services.llm_config import LLMConfig


class OllamaService:
    """
    Service responsible for interacting with the
    Ollama generation API.

    Responsibilities

    • Build generation payload
    • Apply configurable generation settings
    • Measure generation latency
    • Store generation diagnostics

    Future responsibilities

    • Retry handling
    • Streaming support
    • Advanced diagnostics
    """

    def __init__(
        self,
        config: LLMConfig | None = None
    ):

        self.config = config or LLMConfig()

        #
        # Updated after every generation.
        #
        self._last_generation: dict = {}

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    @property
    def last_generation(self) -> dict:

        return self._last_generation.copy()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _build_payload(
        self,
        prompt: str,
        model: str | None,
        temperature: float | None,
        top_p: float | None,
        repeat_penalty: float |None,
        seed: int | None,
        max_tokens: int | None,
        stream: bool | None
    ) -> dict:

        return {
            "model": (
                model
                or self.config.model
                or settings.DEFAULT_MODEL
            ),
            "prompt": prompt,
            "stream": (
                self.config.stream
                if stream is None
                else stream
            ),
            "options": {
                "temperature": (
                    self.config.temperature
                    if temperature is None
                    else temperature
                ),
                "top_p": (
                    self.config.top_p
                    if top_p is None
                    else top_p
                ),
                "repeat_penalty": (
                    self.config.repeat_penalty
                    if repeat_penalty is None
                    else repeat_penalty
                ),
                "seed": (
                    self.config.seed
                    if seed is None
                    else seed
                ),
                "num_predict": (
                    self.config.max_tokens
                    if max_tokens is None
                    else max_tokens
                ),
            },
        }

    def _post_generate(
        self,
        payload: dict
    ) -> requests.Response:

        response = requests.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=self.config.timeout
        )

        response.raise_for_status()

        return response

    def _update_diagnostics(
        self,
        *,
        payload: dict,
        prompt: str,
        response_text: str,
        latency: float
    ) -> None:

        options = payload["options"]

        self._last_generation = {
            "model": payload["model"],
            "temperature": options["temperature"],
            "top_p": options["top_p"],
            "repeat_penalty": options["repeat_penalty"],
            "seed": options["seed"],
            "max_tokens": options["num_predict"],
            "stream": payload["stream"],
            "latency_seconds": latency,
            "prompt_characters": len(prompt),
            "prompt_words": len(prompt.split()),
            "response_characters": len(response_text),
            "response_words": len(response_text.split())
        }

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        repeat_penalty: float | None = None,
        seed: int | None = None,
        max_tokens: int | None = None,
        stream: bool | None = None
    ) -> str:

        payload = self._build_payload(
            prompt=prompt,
            model=model,
            temperature=temperature,
            top_p=top_p,
            repeat_penalty=repeat_penalty,
            seed=seed,
            max_tokens=max_tokens,
            stream=stream
        )

        start = time.perf_counter()

        response = self._post_generate(
            payload
        )

        latency = time.perf_counter() - start

        response_text = response.json()["response"]

        self._update_diagnostics(
            payload=payload,
            prompt=prompt,
            response_text=response_text,
            latency=latency
        )

        return response_text


ollama_service = OllamaService()