from __future__ import annotations

import time

from app.rag.prompt_analyzer import prompt_analyzer
from app.rag.prompt_builder import prompt_builder
from app.rag.prompt_normalizer import prompt_normalizer
from app.rag.prompt_optimizer import prompt_optimizer
from app.rag.prompt_quality import prompt_quality
from app.rag.prompt_renderer import prompt_renderer
from app.rag.prompt_pipeline_models import PromptPipelineResult
from app.rag.token_budget_manager import token_budget_manager


class PromptPipeline:
    """
    Complete prompt construction stage.

    Responsibilities

    • Build prompt components
    • Normalize prompt
    • Analyze prompt
    • Optimize prompt
    • Allocate token budget
    • Render final prompt
    • Evaluate prompt quality

    No retrieval.

    No LLM generation.

    No answer verification.
    """

    def run(
        self,
        *,
        question: str,
        context: str,
        conversation: str | None,
        memory: str,
    ) -> tuple[
        PromptPipelineResult,
        float,
    ]:

        start = time.perf_counter()

        components = prompt_builder.build_prompt(
            question=question,
            context=context,
            conversation=conversation,
            memory=memory,
        )

        components = prompt_normalizer.normalize(
            components,
        )

        analysis = prompt_analyzer.analyze(
            components,
        )

        optimization = prompt_optimizer.optimize(
            components,
        )

        budget = token_budget_manager.allocate(
            optimization.optimized_components,
        )

        prompt = prompt_renderer.render(
            budget.components,
        )

        quality = prompt_quality.analyze(
            analysis=analysis,
            optimization=optimization,
            budget=budget,
        )

        result = PromptPipelineResult(
            prompt=prompt,
            analysis=analysis,
            optimization=optimization,
            budget=budget,
            quality=quality,
        )

        elapsed = (
            time.perf_counter()
            - start
        )

        return (
            result,
            elapsed,
        )


prompt_pipeline = PromptPipeline()