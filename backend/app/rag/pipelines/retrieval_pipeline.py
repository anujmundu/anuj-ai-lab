from __future__ import annotations

import time

from app.rag.context_compressor import context_compressor
from app.rag.intelligence.retrieval_intelligence import (
    retrieval_intelligence,
)
from app.rag.performance_profiler import (
    PerformanceProfiler,
)
from app.rag.ranker import ranker
from app.rag.pipelines.models import (
    RetrievalPipelineResult,
)
from app.rag.builders.diagnostics_builder import (
    diagnostics_builder,
)
from app.rag.query.analyzer import (
    query_analyzer,
)


class RetrievalPipeline:
    """
    Complete retrieval stage.

    Responsibilities

    • Intelligent retrieval
    • Ranking
    • Compression
    • Retrieval diagnostics

    No prompt generation.
    No LLM calls.
    """

    def run(
        self,
        *,
        question: str,
        k: int,
        profiler: PerformanceProfiler | None = None,
    ) -> RetrievalPipelineResult:

        start = time.perf_counter()

        # --------------------------------------------------
        # Query Analysis
        # --------------------------------------------------

        query_analysis = query_analyzer.analyze(
            question,
        )

        # --------------------------------------------------
        # Retrieval
        # --------------------------------------------------

        results = retrieval_intelligence.retrieve(
            query=question,
            k=k,
            analysis=query_analysis,
            profiler=profiler,
        )

        # The retrieval intelligence layer preserves the
        # planner-selected effective K.
        effective_k = results.get(
            "effective_k",
            k,
        )

        # --------------------------------------------------
        # Ranking / Filtering
        # --------------------------------------------------

        results = ranker.filter_results(
            results,
        )

        documents = results["documents"][0]

        metadatas = results["metadatas"][0]

        retrieval = results["retrieval"][0]

        pipeline = results.get(
            "pipeline",
            {},
        )

        # --------------------------------------------------
        # Context Compression
        # --------------------------------------------------

        (
            documents,
            metadatas,
        ) = context_compressor.compress(
            documents=documents,
            metadatas=metadatas,
        )

        # --------------------------------------------------
        # Retrieval Diagnostics
        # --------------------------------------------------

        diagnostics = (
            diagnostics_builder.build_retrieval_diagnostics(
                documents=documents,
                metadatas=metadatas,
                retrieval=retrieval,
                pipeline=pipeline,
                requested_k=k,
                effective_k=effective_k,
                query_analysis=query_analysis,
            )
        )

        # --------------------------------------------------
        # Timing
        # --------------------------------------------------

        retrieval_seconds = (
            time.perf_counter()
            - start
        )

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        return RetrievalPipelineResult(
            documents=documents,
            metadatas=metadatas,
            retrieval=retrieval,
            pipeline=pipeline,
            diagnostics=diagnostics,
            query_analysis=query_analysis,
            requested_k=k,
            effective_k=effective_k,
            retrieval_seconds=retrieval_seconds,
        )

retrieval_pipeline = RetrievalPipeline()