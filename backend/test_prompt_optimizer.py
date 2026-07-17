from app.rag.prompt_optimizer import (
    PromptOptimizer,
    prompt_optimizer,
)
from app.rag.prompt_optimizer_config import PromptOptimizerConfig


def test_prompt_optimizer_normalizes_prompt():
    prompt = "Line 1    \n\n\n\nLine 2      \n"

    optimized = prompt_optimizer.optimize(prompt)

    assert optimized == "Line 1\n\nLine 2"


def test_prompt_optimizer_trims_at_newline():
    optimizer = PromptOptimizer(
        PromptOptimizerConfig(
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