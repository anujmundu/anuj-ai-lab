from __future__ import annotations

from collections import Counter

from app.rag.prompt_optimizer_models import (
    PromptAnalysis,
    PromptComponent,
    PromptComponentType,
)


class PromptAnalyzer:
    """
    Analyzes prompt components and produces statistics.

    This class never modifies prompts.
    """

    def analyze(
        self,
        components: list[PromptComponent],
    ) -> PromptAnalysis:

        if not components:
            return PromptAnalysis()

        total_characters = sum(
            c.characters
            for c in components
        )

        total_tokens = sum(
            c.estimated_tokens
            for c in components
        )

        largest = max(
            components,
            key=lambda c: c.characters,
        )

        ratios: dict[PromptComponentType, float] = {}

        for component in components:

            ratios[
                component.component_type
            ] = (
                component.characters
                / max(total_characters, 1)
            )

        recommendations = []

        balanced = True

        if ratios.get(
            PromptComponentType.CONTEXT,
            0.0,
        ) > 0.75:
            balanced = False
            recommendations.append(
                f"Retrieved context occupies "
                f"{ratios[PromptComponentType.CONTEXT] * 100:.1f}% "
                "of the prompt."
            )

        if ratios.get(
            PromptComponentType.SYSTEM,
            0.0,
        ) < 0.05:
            recommendations.append(
                f"System instructions occupy only "
                f"{ratios[PromptComponentType.SYSTEM] * 100:.1f}% "
                "of the prompt."
            )

        if ratios.get(
            PromptComponentType.QUESTION,
            0.0,
        ) < 0.02:
            recommendations.append(
                f"Question occupies only "
                f"{ratios[PromptComponentType.QUESTION] * 100:.1f}% "
                "of the prompt."
            )

        redundancy = self._redundancy_score(
            components,
        )

        efficiency = max(
            0.0,
            1.0 - redundancy,
        )

        return PromptAnalysis(
            total_tokens=total_tokens,
            total_characters=total_characters,
            instruction_ratio=ratios.get(
                PromptComponentType.SYSTEM,
                0.0,
            ),
            context_ratio=ratios.get(
                "context",
                0.0,
            ),
            memory_ratio=ratios.get(
                "memory",
                0.0,
            ),
            conversation_ratio=ratios.get(
                "conversation",
                0.0,
            ),
            question_ratio=ratios.get(
                "question",
                0.0,
            ),
            largest_component=largest.component_type.value,
            efficiency_score=efficiency,
            redundancy_score=redundancy,
            balanced=balanced,
            recommendations=recommendations,
        )

    def _redundancy_score(
        self,
        components: list[PromptComponent],
    ) -> float:

        texts = [
            c.text.strip()
            for c in components
            if c.text.strip()
        ]

        if not texts:
            return 0.0

        counts = Counter(texts)

        duplicates = sum(
            count - 1
            for count in counts.values()
            if count > 1
        )

        return duplicates / len(texts)


prompt_analyzer = PromptAnalyzer()