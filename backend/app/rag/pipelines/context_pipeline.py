from __future__ import annotations

import time

from app.rag.context_builder import context_builder
from app.rag.pipelines.models import ContextPipelineResult


class ContextPipeline:
    """
    Builds the final retrieval context.

    Responsibilities

    • Build structured context
    • Measure build time

    Does NOT perform prompting or generation.
    """

    def run(
        self,
        *,
        documents: list[str],
        metadatas: list[dict],
    ) -> ContextPipelineResult:

        start = time.perf_counter()

        context = context_builder.build_context(
            documents=documents,
            metadatas=metadatas,
        )

        context_build_seconds = (
            time.perf_counter() - start
        )

        return ContextPipelineResult(
            context=context,
            context_build_seconds=context_build_seconds,
        )


context_pipeline = ContextPipeline()