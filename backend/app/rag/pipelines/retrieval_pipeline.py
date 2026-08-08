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
        
        query_analysis = query_analyzer.analyze(
            question,
        )

        results = retrieval_intelligence.retrieve(
            query=question,
            k=k,
            profiler=profiler,
        )

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

        (
            documents,
            metadatas,
        ) = context_compressor.compress(
            documents=documents,
            metadatas=metadatas,
        )

        diagnostics = (
            diagnostics_builder.build_retrieval_diagnostics(
                documents=documents,
                metadatas=metadatas,
                retrieval=retrieval,
                pipeline=pipeline,
                requested_k=k,
                query_analysis=query_analysis,
            )
        )

        retrieval_seconds = (
            time.perf_counter()
            - start
        )

        return RetrievalPipelineResult(
            documents=documents,
            metadatas=metadatas,
            retrieval=retrieval,
            pipeline=pipeline,
            diagnostics=diagnostics,
            query_analysis=query_analysis,
            retrieval_seconds=retrieval_seconds,
        )


retrieval_pipeline = RetrievalPipeline()