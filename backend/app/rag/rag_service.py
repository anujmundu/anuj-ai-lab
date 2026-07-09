import time

from app.rag.answer_processor import answer_processor
from app.rag.citation_processor import citation_processor
from app.rag.context_builder import context_builder
from app.rag.hallucination_detector import hallucination_detector
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

    def _update_request_diagnostics(
        self,
        *,
        question: str,
        retrieval_seconds: float,
        context_build_seconds: float,
        prompt_build_seconds: float,
        generation_seconds: float,
        total_seconds: float,
        prompt: str,
        answer: str,
        confidence: float,
        hallucination_result: dict | None = None,
        citation_result: dict | None = None,
    ) -> None:

        self._last_request = {

            "question": question,

            "timings": {

                "retrieval_seconds": retrieval_seconds,

                "context_build_seconds": (
                    context_build_seconds
                ),

                "prompt_build_seconds": (
                    prompt_build_seconds
                ),

                "generation_seconds": (
                    generation_seconds
                ),

                "total_seconds": total_seconds,
            },

            "prompt": {

                "characters": len(prompt),

                "words": len(
                    prompt.split()
                ),
            },

            "response": {

                "characters": len(answer),

                "words": len(
                    answer.split()
                ),
            },

            "confidence": confidence,

            "hallucination": (
                hallucination_result
            ),

            "citations": (
                citation_result
            ),
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
    
    def _retrieve_documents(
        self,
        *,
        question: str,
        k: int,
    ) -> tuple[list[str], list[dict], float]:
        """
        Retrieve and rank documents.

        Returns
        -------
        (
            documents,
            metadatas,
            retrieval_seconds,
        )
        """

        start = time.perf_counter()

        results = hybrid_retriever.retrieve(
            query=question,
            k=k,
        )

        results = ranker.filter_results(
            results,
        )

        retrieval_seconds = self._elapsed(
            start,
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        return (
            documents,
            metadatas,
            retrieval_seconds,
        )
        
    def _build_context(
        self,
        *,
        documents: list[str],
        metadatas: list[dict],
    ) -> tuple[str, float]:
        """
        Build structured context from retrieved documents.

        Returns
        -------
        (
            context,
            context_build_seconds,
        )
        """

        start = time.perf_counter()

        context = context_builder.build_context(
            documents=documents,
            metadatas=metadatas,
        )

        context_build_seconds = self._elapsed(
            start,
        )

        return (
            context,
            context_build_seconds,
        )   
        
    def _build_prompt(
        self,
        *,
        question: str,
        context: str,
        conversation: str | None,
        memory: str,
    ) -> tuple[str, float]:
        """
        Build the final LLM prompt.

        Returns
        -------
        (
            prompt,
            prompt_build_seconds,
        )
        """

        start = time.perf_counter()

        prompt = prompt_builder.build_prompt(
            question=question,
            context=context,
            conversation=conversation,
            memory=memory,
        )

        prompt_build_seconds = self._elapsed(
            start,
        )

        return (
            prompt,
            prompt_build_seconds,
        ) 
    
    def _generate_answer(
        self,
        *,
        prompt: str,
    ) -> tuple[str, float]:
        """
        Generate an answer from the language model.

        Returns
        -------
        (
            raw_answer,
            generation_seconds,
        )
        """

        raw_answer = ollama_service.generate(
            prompt=prompt,
        )

        generation_seconds = (
            ollama_service.last_generation.get(
                "latency_seconds",
                0.0,
            )
        )

        return (
            raw_answer,
            generation_seconds,
        )
        
    def _process_answer(
        self,
        *,
        raw_answer: str,
        context: str,
        sources: list[dict],
    ) -> tuple[
        str,
        float,
        dict,
        dict,
    ]:
        """
        Process the generated answer and run
        post-generation analysis.
        """

        processed_answer = (
            answer_processor.process(
                answer=raw_answer,
                context=context,
            )
        )

        hallucination_result = (
            hallucination_detector.detect(
                answer=processed_answer["answer"],
                context=context,
            )
        )

        citation_result = (
            citation_processor.process(
                answer=processed_answer["answer"],
                sources=sources,
            )
        )

        answer = citation_result["answer"]

        confidence = processed_answer["confidence"]

        return (
            answer,
            confidence,
            hallucination_result,
            citation_result,
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

        return ""    

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

        # --------------------------------------------------
        # Retrieval + Ranking
        # --------------------------------------------------

        (
            documents,
            metadatas,
            retrieval_seconds,
        ) = self._retrieve_documents(
            question=question,
            k=k,
        )

        # --------------------------------------------------
        # Context Builder
        # --------------------------------------------------

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

        (
            prompt,
            prompt_build_seconds,
        ) = self._build_prompt(
            question=question,
            context=context,
            conversation=conversation,
            memory=memory,
        )

        # --------------------------------------------------
        # LLM Generation
        # --------------------------------------------------

        (
            raw_answer,
            generation_seconds,
        ) = self._generate_answer(
            prompt=prompt,
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

        (
            answer,
            confidence,
            hallucination_result,
            citation_result,
        ) = self._process_answer(
            raw_answer=raw_answer,
            context=context,
            sources=sources,
        )

        # --------------------------------------------------
        # Total Time
        # --------------------------------------------------

        total_seconds = self._elapsed(
            total_start,
        )

        self._update_request_diagnostics(
            question=question,
            retrieval_seconds=retrieval_seconds,
            context_build_seconds=context_build_seconds,
            prompt_build_seconds=prompt_build_seconds,
            generation_seconds=generation_seconds,
            total_seconds=total_seconds,
            prompt=prompt,
            answer=answer,
            confidence=confidence,
            hallucination_result=hallucination_result,
            citation_result=citation_result,
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