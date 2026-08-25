from app.rag.prompt_normalizer import (
    PromptNormalizer,
    prompt_normalizer,
)
from app.rag.prompt_normalizer_config import PromptNormalizerConfig
from app.rag.prompt_optimizer import (
    PromptOptimizer,
    prompt_optimizer,
)
from app.rag.prompt_optimizer_config import PromptOptimizerConfig
from app.rag.prompt_optimizer_models import (
    PromptComponent,
    PromptComponentType,
)


def test_prompt_normalizer_normalizes_whitespace():
    components = [
        PromptComponent(
            component_type=PromptComponentType.CONTEXT,
            text="Line 1    \n\n\n\nLine 2      \n",
            tokens=10,
            characters=30,
            priority=1,
            required=True,
        ),
    ]

    normalized = prompt_normalizer.normalize(components)

    assert len(normalized) == 1
    assert normalized[0].text == "Line 1\n\nLine 2"


def test_prompt_optimizer_removes_duplicates():
    config = PromptOptimizerConfig(
        enable_optimization=True,
        remove_duplicate_components=True,
    )
    optimizer = PromptOptimizer(config)

    components = [
        PromptComponent(
            component_type=PromptComponentType.CONTEXT,
            text="Chunk A",
            tokens=5,
            characters=7,
            priority=1,
            required=True,
        ),
        PromptComponent(
            component_type=PromptComponentType.CONTEXT,
            text="Chunk A",
            tokens=5,
            characters=7,
            priority=1,
            required=True,
        ),
    ]

    result = optimizer.optimize(components)

    assert len(result.optimized_components) == 1
    assert any(
        opt.rule_name == "remove_duplicate_components"
        for opt in result.optimizations
    )