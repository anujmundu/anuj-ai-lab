
import time

from app.rag.performance_profiler import PerformanceProfiler
from app.rag.enums import PerformanceStageName

from app.rag.prompt_pipeline_models import PromptPipelineResult
from app.rag.token_estimator import token_estimator
from app.services.ollama_service import ollama_service
from app.rag.pipelines.retrieval_pipeline import (
    retrieval_pipeline,
)
from app.rag.pipelines.context_pipeline import (
    context_pipeline,
)
from app.rag.pipelines.prompt_pipeline import (
    prompt_pipeline,
)
from app.rag.pipelines.generation_pipeline import (
    generation_pipeline,
)
from app.rag.pipelines.post_processing_pipeline import (
    post_processing_pipeline,
)
from app.rag.builders.diagnostics_builder import (
    diagnostics_builder,
)
from app.rag.pipelines.memory_pipeline import (
    memory_pipeline,
)
from app.rag.pipelines.evaluation_pipeline import (
    evaluation_pipeline,
)
from app.rag.builders.source_builder import (
    source_builder,
)


class RAGService:
    """
    Orchestrates the complete Retrieval-Augmented
    Generation (RAG) pipeline.

    Responsibilities

    • Retrieval
    • Ranking
    • Context building
    • Prompt construction
    • LLM generation
    • Answer post-processing
    • Hallucination detection
    • Source attribution

    Future responsibilities

    • Conversation memory
    • Streaming
    • Pipeline diagnostics API
    """

    def __init__(self):

        self._last_request: dict = {}

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    @property
    def last_request(self) -> dict:

        return self._last_request.copy()

    def diagnostics(self) -> dict:
        """
        Return the latest RAG pipeline diagnostics.

        If no request has been processed yet,
        return an informative response.
        """

        if not self._last_request:

            return {
                "message": (
                    "No RAG requests have been processed yet."
                ),
                "request": {},
                "generation": {}
            }

        return {
            "request": self.last_request,
            "generation": (
                ollama_service.last_generation.copy()
            )
        }

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _elapsed(
        self,
        start: float
    ) -> float:

        return time.perf_counter() - start
        
    def _build_context(
        self,
        *,
        documents: list[str],
        metadatas: list[dict],
    ):

        result = context_pipeline.run(
            documents=documents,
            metadatas=metadatas,
        )

        return (
            result.context,
            result.context_build_seconds,
        )
        
    def _build_prompt(
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

        return prompt_pipeline.run(
            question=question,
            context=context,
            conversation=conversation,
            memory=memory,
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def ask(
        self,
        question: str,
        conversation: str | None = None,
        k: int = 3,
    ) -> dict:

        total_start = time.perf_counter()
        
        profiler = PerformanceProfiler()

        # --------------------------------------------------
        # Retrieval + Ranking
        # --------------------------------------------------

        with profiler.measure(
            PerformanceStageName.RETRIEVAL
        ):
            retrieval_result = retrieval_pipeline.run(
                question=question,
                k=k,
                profiler=profiler,
            )

            documents = retrieval_result.documents

            metadatas = retrieval_result.metadatas

            retrieval = retrieval_result.retrieval

            pipeline = retrieval_result.pipeline

            retrieval_seconds = retrieval_result.retrieval_seconds

            retrieval_diagnostics = retrieval_result.diagnostics

        # --------------------------------------------------
        # Context Builder
        # --------------------------------------------------

        with profiler.measure(
            PerformanceStageName.CONTEXT_BUILDER
        ):
            (
                context,
                context_build_seconds,
            ) = self._build_context(
                documents=documents,
                metadatas=metadatas,
            )

        memory = memory_pipeline.prepare(
            question=question,
            conversation=conversation,
        )

        # --------------------------------------------------
        # Prompt Builder
        # --------------------------------------------------

        with profiler.measure(
            PerformanceStageName.PROMPT_BUILDER
        ):
            (
                prompt_pipeline,
                prompt_build_seconds,
            ) = self._build_prompt(
                question=question,
                context=context,
                conversation=conversation,
                memory=memory,
            )

        prompt = prompt_pipeline.prompt

        # --------------------------------------------------
        # LLM Generation
        # --------------------------------------------------

        generation_result = (
            generation_pipeline.run(
                prompt=prompt,
                profiler=profiler,
            )
        )

        raw_answer = (
            generation_result.raw_answer
        )

        generation_seconds = (
            generation_result.generation_seconds
        )

        # --------------------------------------------------
        # Sources
        # --------------------------------------------------

        sources = source_builder.build(
            metadatas,
        )

        # --------------------------------------------------
        # Answer Processing
        # --------------------------------------------------

        post_processing_result = (
            post_processing_pipeline.run(
                raw_answer=raw_answer,
                context=context,
                sources=sources,
                documents=documents,
                metadatas=metadatas,
                profiler=profiler,
            )
        )

        answer = post_processing_result.answer

        confidence = post_processing_result.confidence

        alignment = post_processing_result.alignment

        hallucination_result = (
            post_processing_result.hallucination
        )

        consistency_result = (
            post_processing_result.consistency
        )

        answer_quality_result = (
            post_processing_result.answer_quality
        )

        citation_result = (
            post_processing_result.citation_result
        )

        evaluation_result = (
            evaluation_pipeline.run(
                retrieval_quality=(
                    retrieval_diagnostics["quality"]
                ),
                prompt_quality=(
                    prompt_pipeline.quality
                ),
                answer_quality=(
                    answer_quality_result
                ),
                hallucination=(
                    hallucination_result
                ),
                citations=(
                    citation_result
                ),
            )
        )

        pipeline_health_result = (
            evaluation_result.pipeline_health
        )

        scorecard_result = (
            evaluation_result.scorecard
        )

        # --------------------------------------------------
        # Total Time
        # --------------------------------------------------

        total_seconds = self._elapsed(
            total_start,
        )
        
        performance = profiler.build_result()

        self._last_request = (
            diagnostics_builder.build_request_diagnostics(
                question=question,
                retrieval_seconds=retrieval_seconds,
                retrieval_diagnostics=retrieval_diagnostics,
                context_build_seconds=context_build_seconds,
                prompt_build_seconds=prompt_build_seconds,
                generation_seconds=generation_seconds,
                total_seconds=total_seconds,
                prompt_pipeline=prompt_pipeline,
                prompt=prompt,
                context=context,
                memory=memory,
                conversation=conversation,
                answer=answer,
                confidence=confidence,
                hallucination_result=hallucination_result,
                consistency_result=consistency_result,
                answer_quality_result=answer_quality_result,
                pipeline_health_result=pipeline_health_result,
                scorecard_result=scorecard_result,
                citation_result=citation_result,
                performance=performance,
            )
        )

        memory_pipeline.store(
            question=question,
        )

        # --------------------------------------------------
        # API Response
        # --------------------------------------------------

        return {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "sources": sources,
        }


rag_service = RAGService()
