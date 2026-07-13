import time

from app.rag.answer_processor import answer_processor
from app.rag.citation_processor import citation_processor
from app.rag.citation_inserter import citation_inserter
from app.rag.context_builder import context_builder
from app.rag.context_compressor import context_compressor
from app.rag.hallucination_detector import hallucination_detector
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.prompt_builder import prompt_builder
from app.rag.ranker import ranker
from app.rag.token_estimator import token_estimator
from app.services.ollama_service import ollama_service
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

    def _update_request_diagnostics(
        self,
        *,
        question: str,
        retrieval_seconds: float,
        retrieval_diagnostics: dict,
        context_build_seconds: float,
        prompt_build_seconds: float,
        generation_seconds: float,
        total_seconds: float,
        prompt: str,
        context: str,
        memory: str,
        conversation: str | None,
        answer: str,
        confidence: float,
        hallucination_result: dict | None = None,
        citation_result: dict | None = None,
    ) -> None:
        
        
        template = (
            prompt
            .replace(context, "", 1)
            .replace(memory, "", 1)
            .replace(question, "", 1)
        )

        template = (
            template.replace(
                conversation or "",
                "",
                1,
            )
        )

        prompt_tokens = token_estimator.estimate(
            prompt,
        )

        template_tokens = token_estimator.estimate(
            template,
        )

        context_tokens = token_estimator.estimate(
            context,
        )

        memory_tokens = token_estimator.estimate(
            memory,
        )

        question_tokens = token_estimator.estimate(
            question,
        )

        conversation_tokens = token_estimator.estimate(
            conversation,
        )

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
            
            "retrieval": retrieval_diagnostics,

            "prompt": {

                "characters": len(prompt),

                "words": len(
                    prompt.split()
                ),

                "estimated_tokens": prompt_tokens,

                "composition": {

                    "template_characters": (
                        len(prompt)
                        - len(context)
                        - len(memory)
                        - len(question)
                    ),

                    "template_words": (
                        len(prompt.split())
                        - len(context.split())
                        - len(memory.split())
                        - len(question.split())
                    ),
                    
                    "template_tokens": template_tokens,

                    "context_characters": len(context),

                    "context_words": len(
                        context.split()
                    ),
                    
                    "context_tokens": context_tokens,

                    "memory_characters": len(memory),

                    "memory_words": len(
                        memory.split()
                    ),
                    
                    "memory_tokens": memory_tokens,

                    "question_characters": len(question),

                    "question_words": len(
                        question.split()
                    ),
                    
                    "question_tokens": question_tokens,

                    "conversation_characters": (
                        len(conversation)
                        if conversation
                        else 0
                    ),

                    "conversation_words": (
                        len(conversation.split())
                        if conversation
                        else 0
                    ),
                    
                    "conversation_tokens": conversation_tokens,
                },
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
        
    def _build_retrieval_diagnostics(
        self,
        *,
        documents: list[str],
        metadatas: list[dict],
        retrieval: list[dict],
        pipeline: dict,
        requested_k: int,
    ) -> dict:
        """
        Build retrieval diagnostics after ranking and
        context compression.
        """
        
        confidence = self._retrieval_confidence(
            retrieval,
        )

        return {
            **pipeline,
            
            "confidence": confidence,

            "requested_k": requested_k,

            "retrieved_documents": len(documents),

            "documents": [
                {
                    "filename": metadata["filename"],
                    "chunk_id": metadata["chunk_id"],
                    "chunk_number": metadata["chunk_number"],
                    "total_chunks": metadata["total_chunks"],

                    "semantic_score": scores["semantic_score"],
                    "keyword_score": scores["keyword_score"],
                    "combined_score": scores["combined_score"],

                    "semantic_rank": scores["semantic_rank"],
                    "keyword_rank": scores["keyword_rank"],
                }
                for metadata, scores in zip(
                    metadatas,
                    retrieval,
                )
            ],
        }
        
    def _retrieval_confidence(
        self,
        retrieval: list[dict],
    ) -> dict:
        """
        Compute confidence metrics for retrieved
        documents based on combined scores.
        """

        if not retrieval:
            return {
                "average_similarity": 0.0,
                "minimum_similarity": 0.0,
                "maximum_similarity": 0.0,
                "score_variance": 0.0,
                "retrieval_confidence": "None",
            }

        scores = [
            item["combined_score"]
            for item in retrieval
        ]

        average = sum(scores) / len(scores)

        minimum = min(scores)

        maximum = max(scores)

        variance = (
            sum(
                (score - average) ** 2
                for score in scores
            )
            / len(scores)
        )

        if average >= 0.75:
            confidence = "High"

        elif average >= 0.50:
            confidence = "Medium"

        else:
            confidence = "Low"

        return {

            "average_similarity": round(
                average,
                3,
            ),

            "minimum_similarity": round(
                minimum,
                3,
            ),

            "maximum_similarity": round(
                maximum,
                3,
            ),

            "score_variance": round(
                variance,
                4,
            ),

            "retrieval_confidence": confidence,
        }
        
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

        citation_insert_result = (
            citation_inserter.insert(
                answer=processed_answer["answer"],
                sources=sources,
            )
        )

        hallucination_result = (
            hallucination_detector.detect(
                answer=citation_insert_result["answer"],
                context=context,
            )
        )

        citation_result = (
            citation_processor.process(
                answer=citation_insert_result["answer"],
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

        # --------------------------------------------------
        # Retrieval + Ranking
        # --------------------------------------------------

        (
            documents,
            metadatas,
            retrieval,
            pipeline,
            retrieval_seconds,
        ) = self._retrieve_documents(
            question=question,
            k=k,
        )
        
        (
            documents,
            metadatas,
        ) = context_compressor.compress(
            documents=documents,
            metadatas=metadatas,
        )
        
        retrieval_diagnostics = (
            self._build_retrieval_diagnostics(
                documents=documents,
                metadatas=metadatas,
                retrieval=retrieval,
                pipeline=pipeline,
                requested_k=k,
            )
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
            retrieval_diagnostics=retrieval_diagnostics,
            context_build_seconds=context_build_seconds,
            prompt_build_seconds=prompt_build_seconds,
            generation_seconds=generation_seconds,
            total_seconds=total_seconds,
            prompt=prompt,
            context=context,
            memory=memory,
            conversation=conversation,
            answer=answer,
            confidence=confidence,
            hallucination_result=hallucination_result,
            citation_result=citation_result,
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