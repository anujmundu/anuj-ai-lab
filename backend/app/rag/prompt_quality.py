from app.rag.prompt_quality_config import (
    PromptQualityConfig,
)


class PromptQuality:
    """
    Computes diagnostics describing how the prompt
    is composed.

    Responsibilities

    • Component ratios
    • Balance estimation
    • Largest component
    • Prompt efficiency
    """

    def __init__(
        self,
        config: PromptQualityConfig | None = None,
    ):

        self.config = (
            config
            or PromptQualityConfig()
        )

    def analyze(
        self,
        *,
        template_tokens: int,
        context_tokens: int,
        memory_tokens: int,
        question_tokens: int,
    ) -> dict:

        if not self.config.enabled:

            return {}

        total = (
            template_tokens
            + context_tokens
            + memory_tokens
            + question_tokens
        )

        if total == 0:

            return {
                "context_ratio": 0.0,
                "instruction_ratio": 0.0,
                "memory_ratio": 0.0,
                "question_ratio": 0.0,
                "balanced": True,
                "largest_component": "none",
                "prompt_efficiency": "Unknown",
            }

        ratios = {

            "instruction": (
                template_tokens / total
            ),

            "context": (
                context_tokens / total
            ),

            "memory": (
                memory_tokens / total
            ),

            "question": (
                question_tokens / total
            ),
        }

        largest = max(
            ratios,
            key=ratios.get,
        )

        values = list(
            ratios.values()
        )

        balanced = (
            max(values)
            - min(values)
            <= self.config.balanced_ratio_difference
        )

        context_ratio = ratios["context"]

        if context_ratio >= 0.50:

            efficiency = "Good"

        elif context_ratio >= 0.30:

            efficiency = "Fair"

        else:

            efficiency = "Poor"

        return {

            "context_ratio": round(
                ratios["context"],
                3,
            ),

            "instruction_ratio": round(
                ratios["instruction"],
                3,
            ),

            "memory_ratio": round(
                ratios["memory"],
                3,
            ),

            "question_ratio": round(
                ratios["question"],
                3,
            ),

            "balanced": balanced,

            "largest_component": largest,

            "prompt_efficiency": efficiency,
        }


prompt_quality = PromptQuality()