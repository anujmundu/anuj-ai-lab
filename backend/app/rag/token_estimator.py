import math


class TokenEstimator:
    """
    Lightweight token estimation utility.

    The estimator intentionally avoids model-specific
    tokenizers so it can work with any LLM backend.

    Current approximation

        tokens ≈ characters / 4

    This is sufficiently accurate for diagnostics and
    prompt budgeting.

    Future implementations may replace this with:

    • tiktoken
    • llama tokenizer
    • qwen tokenizer
    • mistral tokenizer

    without changing the public API.
    """

    DEFAULT_CHARACTERS_PER_TOKEN = 4

    def __init__(
        self,
        characters_per_token: int = DEFAULT_CHARACTERS_PER_TOKEN,
    ):

        self.characters_per_token = max(
            1,
            characters_per_token,
        )

    def estimate(
        self,
        text: str | None,
    ) -> int:
        """
        Estimate the number of tokens contained
        in a text string.
        """

        if not text:
            return 0

        return math.ceil(
            len(text)
            / self.characters_per_token
        )


token_estimator = TokenEstimator()