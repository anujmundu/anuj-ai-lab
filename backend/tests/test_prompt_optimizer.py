from backend.app.rag.prompt_normalizer import (
    PromptNormalizer,
    prompt_optimizer,
)
from backend.app.rag.prompt_normalizer_config import PromptOptimizerConfig


def test_prompt_normalizer_normalizes_prompt():
    prompt = "Line 1    \n\n\n\nLine 2      \n"

    optimized = prompt_optimizer.optimize(prompt)

    assert optimized == "Line 1\n\nLine 2"


def test_prompt_normalizer_trims_at_newline():
    optimizer = PromptNormalizer(
        PromptNormalizerConfig(
            max_prompt_characters=15,
        )
    )

    prompt = (
        "Line 1\n"
        "Line 2\n"
        "Line 3\n"
        "Line 4\n"
    )

    optimized = optimizer.optimize(prompt)

    assert optimized == "Line 1\nLine 2"