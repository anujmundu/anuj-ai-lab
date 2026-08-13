from __future__ import annotations

from collections.abc import Callable

from app.rag.evaluation.models import EvaluationSample
from app.rag.evaluation.production_adapter import (
    ProductionRetrievalAdapter,
)
from app.rag.performance_profiler import PerformanceProfiler

from app.rag.pipelines.context_pipeline import (
    ContextPipeline,
    context_pipeline,
)
from app.rag.pipelines.generation_pipeline import (
    GenerationPipeline,
    generation_pipeline,
)
from app.rag.pipelines.post_processing_pipeline import (
    PostProcessingPipeline,
    post_processing_pipeline,
)
from app.rag.pipelines.prompt_pipeline import (
    PromptPipeline,
    prompt_pipeline,
)


class ProductionBenchmarkExecutor:
    """
    Executes one golden evaluation sample through the
    production RAG generation and verification pipeline.

    This class is an orchestration adapter only.

    It does not implement:
    - retrieval
    - context construction
    - prompt construction
    - generation
    - hallucination detection
    - evidence alignment
    - citation processing
    - grounding

    All of those responsibilities remain in the existing
    production pipeline components.
    """

    def __init__(
        self,
        *,
        retrieval_adapter: ProductionRetrievalAdapter | None = None,
        context_pipeline_instance: ContextPipeline | None = None,
        prompt_pipeline_instance: PromptPipeline | None = None,
        generation_pipeline_instance: GenerationPipeline | None = None,
        post_processing_pipeline_instance: (
            PostProcessingPipeline | None
        ) = None,
    ) -> None:

        self.retrieval_adapter = (
            retrieval_adapter
            or ProductionRetrievalAdapter()
        )

        self.context_pipeline = (
            context_pipeline_instance
            or context_pipeline
        )

        self.prompt_pipeline = (
            prompt_pipeline_instance
            or prompt_pipeline
        )

        self.generation_pipeline = (
            generation_pipeline_instance
            or generation_pipeline
        )

        self.post_processing_pipeline = (
            post_processing_pipeline_instance
            or post_processing_pipeline
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _sources(
        metadatas: list[dict],
    ) -> list[dict]:
        """
        Build source metadata using the same metadata shape
        consumed by the production post-processing pipeline.

        This deliberately remains a small adapter rather than
        reimplementing source attribution logic.
        """

        return [
            metadata or {}
            for metadata in metadatas
        ]

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def execute(
        self,
        sample: EvaluationSample,
        *,
        k: int = 10,
        profiler: PerformanceProfiler | None = None,
    ) -> dict:
        """
        Execute one golden sample through production RAG.

        Returns the execution payload expected by BenchmarkService.
        """

        if not isinstance(
            sample,
            EvaluationSample,
        ):
            raise TypeError(
                "sample must be an EvaluationSample"
            )

        if k <= 0:
            raise ValueError(
                "k must be greater than zero"
            )

        # --------------------------------------------------
        # Retrieval
        # --------------------------------------------------

        retrieval_results = (
            self.retrieval_adapter.retrieve(
                sample,
                k=k,
                profiler=profiler,
            )
        )

        documents = [
            result.document
            for result in retrieval_results
        ]

        metadatas = [
            {
                "filename": result.filename,
                "chunk_id": result.chunk_id,
                "chunk_number": result.chunk_number,
                "total_chunks": result.total_chunks,
                "source": result.source,
            }
            for result in retrieval_results
        ]

        retrieval = [
            {
                "semantic_score": result.semantic_score,
                "keyword_score": result.keyword_score,
                "combined_score": result.combined_score,
            }
            for result in retrieval_results
        ]

        # --------------------------------------------------
        # Context
        # --------------------------------------------------

        context_result = (
            self.context_pipeline.run(
                documents=documents,
                metadatas=metadatas,
            )
        )

        context = context_result.context

        # --------------------------------------------------
        # Prompt
        # --------------------------------------------------

        prompt_result, _ = (
            self.prompt_pipeline.run(
                question=sample.question,
                context=context,
                conversation=None,
                memory="",
            )
        )

        # --------------------------------------------------
        # Generation
        # --------------------------------------------------

        generation_result = (
            self.generation_pipeline.run(
                prompt=prompt_result.prompt,
                profiler=profiler,
            )
        )

        # --------------------------------------------------
        # Sources
        # --------------------------------------------------

        sources = self._sources(
            metadatas,
        )

        # --------------------------------------------------
        # Post-processing / verification
        # --------------------------------------------------

        post_result = (
            self.post_processing_pipeline.run(
                raw_answer=generation_result.raw_answer,
                context=context,
                sources=sources,
                documents=documents,
                metadatas=metadatas,
                profiler=profiler,
            )
        )

        return {
            "retrieval": retrieval_results,
            "answer": post_result.answer,
            "confidence": post_result.confidence,
            "alignment": post_result.alignment,
            "grounding": post_result.grounding,
            "hallucination": post_result.hallucination,
            "consistency": post_result.consistency,
            "answer_quality": post_result.answer_quality,
            "citations": post_result.citation_result,
            "prompt_quality": prompt_result.quality,
            "context": context,
            "retrieval_pipeline": {
                "documents": documents,
                "metadatas": metadatas,
            },
        }


production_benchmark_executor = (
    ProductionBenchmarkExecutor()
)
