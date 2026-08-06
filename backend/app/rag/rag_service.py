from ctypes import alignment
import time
from dataclasses import asdict
from contextlib import nullcontext

from app.rag.performance_profiler import PerformanceProfiler
from app.rag.enums import PerformanceStageName
from app.rag.pipeline_health import pipeline_health
from app.rag.rag_scorecard import rag_scorecard
from app.rag.intelligence.retrieval_intelligence import (
    retrieval_intelligence,
)
from app.rag.retrieval_explainer import (retrieval_explainer,)
from app.rag.prompt_pipeline_models import PromptPipelineResult
from app.rag.performance_models import PerformanceProfilingResult
from app.rag.ranker import ranker
from app.rag.retrieval_quality import retrieval_quality
from app.rag.token_estimator import token_estimator
from app.services.ollama_service import ollama_service
from app.rag.evidence_models import (
    EvidenceAlignmentResult,
)
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
from sqlmodel import Session

from app.db.database import engine
from app.memory.manager import MemoryManager


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
    
    def _build_sources(
        self,
        metadatas: list[dict]
    ) -> list[dict]:

        return [
            {
                "filename": metadata["filename"],
                "chunk_id": metadata["chunk_id"],
                "chunk_number": metadata["chunk_number"],
                "total_chunks": metadata["total_chunks"],
            }
            for metadata in metadatas
        ]
    
    def _retrieve_documents(
        self,
        *,
        question: str,
        k: int,
        profiler: PerformanceProfiler | None = None,
    ) -> tuple[
        list[str],
        list[dict],
        list[dict],
        dict,
        float,
    ]:
        """
        Retrieve and rank documents.

        Returns
        -------
        (
            documents,
            metadatas,
            retrieval,
            retrieval_seconds,
        )
        """

        measure = (
            profiler.measure
            if profiler is not None
            else lambda *_: nullcontext()
        )

        start = time.perf_counter()

        results = retrieval_intelligence.retrieve(
            query=question,
            k=k,
            profiler=profiler,
        )

        results = ranker.filter_results(
            results,
        )

        retrieval_seconds = self._elapsed(
            start,
        )

        documents = results["documents"][0]
        
        metadatas = results["metadatas"][0]
        
        retrieval = results["retrieval"][0]
        
        pipeline = results.get(
            "pipeline",
            {}
        )

        return (
            documents,
            metadatas,
            retrieval,
            pipeline,
            retrieval_seconds,
        )
        
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
        
    def _prepare_memory(
        self,
        question: str,
        conversation: str | None,
    ) -> str:
        """
        Prepare persistent memory for prompt construction.

        Conversation support is reserved for future
        conversation-specific memory retrieval.
        """

        with Session(engine) as session:

            manager = MemoryManager(
                session=session,
            )

            return manager.relevant_context(
                query=question,
            )
            
    def _store_memory(
        self,
        question: str,
    ) -> None:
        """
        Extract and persist useful user memories.

        This currently stores only the user's message.
        Future versions may also process assistant
        responses and conversation history.
        """

        with Session(engine) as session:

            manager = MemoryManager(
                session=session,
            )

            manager.process(
                question,
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

        memory = self._prepare_memory(
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

        sources = self._build_sources(
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

        # --------------------------------------------------
        # Pipeline Health
        # --------------------------------------------------

        pipeline_health_result = (
            pipeline_health.evaluate(
                retrieval_quality=(
                    retrieval_diagnostics["quality"]
                ),
                hallucination=hallucination_result,
                answer_quality=answer_quality_result,
                citation_result=citation_result,
            )
        )

        # --------------------------------------------------
        # RAG Scorecard
        # --------------------------------------------------

        scorecard_result = rag_scorecard.build(
            retrieval_quality=retrieval_diagnostics["quality"],
            prompt_quality=prompt_pipeline.quality,
            answer_quality=answer_quality_result,
            hallucination=hallucination_result,
            citations=citation_result,
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

        self._store_memory(
            question,
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
