from __future__ import annotations

from copy import deepcopy

from app.rag.prompt_analyzer import prompt_analyzer
from app.rag.prompt_optimizer_config import PromptOptimizerConfig
from app.rag.prompt_optimizer_models import (
    PromptAnalysis,
    PromptComponent,
    PromptOptimization,
    PromptOptimizationResult,
)


class PromptOptimizer:
    """
    Performs deterministic optimization on PromptComponents.

    Responsibilities
    ----------------
    - Remove duplicate components
    - Remove empty components
    - Sort components by priority
    - Produce before/after analysis

    This optimizer NEVER rewrites prompt content.
    """

    def __init__(
        self,
        config: PromptOptimizerConfig | None = None,
    ):
        self.config = config or PromptOptimizerConfig()

    def optimize(
        self,
        components: list[PromptComponent],
    ) -> PromptOptimizationResult:
        """
        Optimize prompt components.

        Parameters
        ----------
        components
            Prompt components produced by PromptBuilder.

        Returns
        -------
        PromptOptimizationResult
        """

        original_components = deepcopy(components)

        analysis_before = prompt_analyzer.analyze(
            original_components,
        )

        if not self.config.enable_optimization:

            return PromptOptimizationResult(
                original_components=original_components,
                optimized_components=deepcopy(original_components),
                analysis_before=analysis_before,
                analysis_after=analysis_before,
                optimizations=[],
                tokens_saved=0,
            )

        optimized = deepcopy(original_components)

        optimizations: list[PromptOptimization] = []

        if self.config.remove_duplicate_components:
            optimized, optimization = self._remove_duplicate_components(
                optimized,
            )

            if optimization:
                optimizations.append(
                    optimization,
                )

        if self.config.remove_empty_components:
            optimized, optimization = self._remove_empty_components(
                optimized,
            )

            if optimization:
                optimizations.append(
                    optimization,
                )

        if self.config.sort_by_priority:
            optimized, optimization = self._sort_components(
                optimized,
            )

            if optimization:
                optimizations.append(
                    optimization,
                )

        analysis_after = prompt_analyzer.analyze(
            optimized,
        )

        tokens_saved = max(
            0,
            analysis_before.total_tokens
            - analysis_after.total_tokens,
        )

        return PromptOptimizationResult(
            original_components=original_components,
            optimized_components=optimized,
            analysis_before=analysis_before,
            analysis_after=analysis_after,
            optimizations=optimizations,
            tokens_saved=tokens_saved,
        )

    def _remove_duplicate_components(
        self,
        components: list[PromptComponent],
    ) -> tuple[
        list[PromptComponent],
        PromptOptimization | None,
    ]:
        """
        Remove duplicated prompt components.
        """

        seen: set[
            tuple[str, str]
        ] = set()

        unique_components: list[
            PromptComponent
        ] = []

        removed = 0

        for component in components:

            key = (
                component.component_type.value,
                component.text.strip(),
            )

            if key in seen:

                removed += 1
                continue

            seen.add(key)

            unique_components.append(
                component,
            )

        if removed == 0:
            return unique_components, None

        return (
            unique_components,
            PromptOptimization(
                rule_name="remove_duplicate_components",
                description=(
                    f"Removed {removed} duplicate prompt "
                    "component(s)."
                ),
            ),
        )

    def _remove_empty_components(
        self,
        components: list[PromptComponent],
    ) -> tuple[
        list[PromptComponent],
        PromptOptimization | None,
    ]:
        """
        Remove empty prompt components.
        """

        filtered: list[
            PromptComponent
        ] = []

        removed = 0

        minimum = (
            self.config.minimum_component_characters
        )

        for component in components:

            if (
                self.config.preserve_required_components
                and component.required
            ):
                filtered.append(component)
                continue

            if len(component.text.strip()) < minimum:
                removed += 1
                continue

            filtered.append(component)

        if removed == 0:
            return filtered, None

        return (
            filtered,
            PromptOptimization(
                rule_name="remove_empty_components",
                description=(
                    f"Removed {removed} empty prompt "
                    "component(s)."
                ),
            ),
        )

    def _sort_components(
        self,
        components: list[PromptComponent],
    ) -> tuple[
        list[PromptComponent],
        PromptOptimization | None,
    ]:
        """
        Sort prompt components by priority.
        """

        sorted_components = sorted(
            components,
            key=lambda component: component.priority,
        )

        return (
            sorted_components,
            PromptOptimization(
                rule_name="sort_by_priority",
                description=(
                    "Sorted prompt components by priority."
                ),
            ),
        )


prompt_optimizer = PromptOptimizer()