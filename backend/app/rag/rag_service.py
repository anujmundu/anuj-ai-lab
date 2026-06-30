import time

from app.rag.answer_processor import answer_processor
from app.rag.citation_processor import citation_processor
from app.rag.context_builder import context_builder
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.prompt_builder import prompt_builder
from app.rag.ranker import ranker
from app.services.ollama_service import ollama_service


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

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _elapsed(
        self,
        start: float
    ) -> float:

        return time.perf_counter() - start

    def _update_request_diagnostics(
        self,
        *,
        retrieval_seconds: float,
        context_build_seconds: float,
        prompt_build_seconds: float,
        generation_seconds: float,
        total_seconds: float
    ) -> None:

        self._last_request = {
            "retrieval_seconds": retrieval_seconds,
            "context_build_seconds": context_build_seconds,
            "prompt_build_seconds": prompt_build_seconds,
            "generation_seconds": generation_seconds,
            "total_seconds": total_seconds,
        }

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

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def ask(
        self,
        question: str,
        k: int = 3
    ) -> dict:

        total_start = time.perf_counter()

        # --------------------------------------------------
        # Retrieval + Ranking
        # --------------------------------------------------

        start = time.perf_counter()

        results = hybrid_retriever.retrieve(
            query=question,
            k=k
        )

        results = ranker.filter_results(
            results
        )

        retrieval_seconds = self._elapsed(start)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        # --------------------------------------------------
        # Context Builder
        # --------------------------------------------------

        start = time.perf_counter()

        context = context_builder.build_context(
            documents=documents,
            metadatas=metadatas
        )

        context_build_seconds = self._elapsed(start)

        # --------------------------------------------------
        # Prompt Builder
        # --------------------------------------------------

        start = time.perf_counter()

        prompt = prompt_builder.build_prompt(
            question=question,
            context=context
        )

        prompt_build_seconds = self._elapsed(start)

        # --------------------------------------------------
        # LLM Generation
        # --------------------------------------------------

        raw_answer = ollama_service.generate(
            prompt=prompt
        )

        generation_seconds = (
            ollama_service.last_generation.get(
                "latency_seconds",
                0.0
            )
        )

        # --------------------------------------------------
        # Sources
        # --------------------------------------------------

        sources = self._build_sources(
            metadatas
        )

        # --------------------------------------------------
        # Answer Processor
        # --------------------------------------------------

        processed_answer = answer_processor.process(
            answer=raw_answer,
            context=context
        )

        # --------------------------------------------------
        # Citation Processor
        # --------------------------------------------------

        citation_result = citation_processor.process(
            answer=processed_answer["answer"],
            sources=sources
        )

        answer = citation_result["answer"]

        # --------------------------------------------------
        # Total Time
        # --------------------------------------------------

        total_seconds = self._elapsed(
            total_start
        )

        self._update_request_diagnostics(
            retrieval_seconds=retrieval_seconds,
            context_build_seconds=context_build_seconds,
            prompt_build_seconds=prompt_build_seconds,
            generation_seconds=generation_seconds,
            total_seconds=total_seconds,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": sources,
        }


rag_service = RAGService()