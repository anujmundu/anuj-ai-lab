from dataclasses import dataclass


@dataclass(slots=True)
class LLMConfig:
    """
    Configuration for the language model service.

    Controls how prompts are sent to the model
    without affecting the rest of the RAG pipeline.
    """

    # --------------------------------------------------
    # Model
    # --------------------------------------------------

    model: str | None = None

    # --------------------------------------------------
    # Generation
    # --------------------------------------------------

    temperature: float = 0.2

    top_p: float = 0.9

    repeat_penalty: float = 1.1

    seed: int = 42

    max_tokens: int = 512

    stream: bool = False

    # --------------------------------------------------
    # Networking
    # --------------------------------------------------

    timeout: int = 300

    retry_count: int = 1