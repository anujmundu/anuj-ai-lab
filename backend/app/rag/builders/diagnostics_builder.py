from dataclasses import asdict

from app.rag.performance_models import (
    PerformanceProfilingResult,
)

from app.rag.prompt_pipeline_models import (
    PromptPipelineResult,
)

from app.rag.retrieval_quality import (
    retrieval_quality,
)

from app.rag.retrieval_explainer import (
    retrieval_explainer,
)

from app.rag.token_estimator import (
    token_estimator,
)
from app.rag.query.models import QueryAnalysisResult

class DiagnosticsBuilder:
    """
    Builds retrieval diagnostics and request diagnostics
    for the RAG pipeline.
    """

    def build_retrieval_diagnostics(
        self,
        *,
        query_analysis: QueryAnalysisResult,
        requested_k: int,
        effective_k: int,
        documents: list[str],
        metadatas: list[dict],
        retrieval: list[dict],
        pipeline: dict,
    ):
        return self._build_retrieval_diagnostics(
            documents=documents,
            metadatas=metadatas,
            retrieval=retrieval,
            pipeline=pipeline,
            requested_k=requested_k,
            effective_k=effective_k,
            query_analysis=query_analysis,
        )

    def build_request_diagnostics(
        self,
        query_analysis: QueryAnalysisResult,
        **kwargs,
    ):
        return self._update_request_diagnostics(
            query_analysis=query_analysis,
            **kwargs,
        )

    # ----------------------------
    # private implementation below
    # ----------------------------

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

    def _build_retrieval_diagnostics(
        self,
        *,
        documents: list[str],
        metadatas: list[dict],
        retrieval: list[dict],
        pipeline: dict,
        requested_k: int,
        effective_k: int,
        query_analysis: QueryAnalysisResult,
    ) -> dict:
        """
        Build retrieval diagnostics after ranking and
        context compression.

        requested_k represents the caller's requested retrieval
        depth.

        effective_k represents the retrieval depth selected by
        the retrieval planner.
        """

        confidence = self._retrieval_confidence(
            retrieval,
        )

        quality = retrieval_quality.evaluate(
            retrieval=retrieval,
            metadatas=metadatas,
        )

        return {
            **pipeline,

            "confidence": confidence,

            "quality": quality,

            "requested_k": requested_k,

            "effective_k": effective_k,

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

                    "selected_because": (
                        retrieval_explainer.explain(
                            scores,
                        )
                    ),
                }
                for metadata, scores in zip(
                    metadatas,
                    retrieval,
                )
            ],

            "query": {
                "text": query_analysis.query,
                "intent": query_analysis.intent.value,
                "complexity": query_analysis.complexity.value,
                "ambiguity": query_analysis.ambiguity.value,
                "requires_rewrite": (
                    query_analysis.requires_rewrite
                ),
                "requires_multi_query": (
                    query_analysis.requires_multi_query
                ),
            },
        }

    def _update_request_diagnostics(
            self,
            *,
            query_analysis: QueryAnalysisResult,
            question: str,
            retrieval_seconds: float,
            retrieval_diagnostics: dict,
            context_build_seconds: float,
            prompt_build_seconds: float,
            generation_seconds: float,
            total_seconds: float,
            prompt_pipeline: PromptPipelineResult,
            prompt: str,
            context: str,
            memory: str,
            conversation: str | None,
            answer: str,
            confidence: float,
            hallucination_result: dict | None = None,
            consistency_result: dict | None = None,
            answer_quality_result: dict | None = None,
            pipeline_health_result: dict | None = None,
            scorecard_result: dict | None = None,
            citation_result: dict | None = None,
            grounding_result: dict | None = None,
            performance: PerformanceProfilingResult,
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

            return {

                "question": question,

                "query": {
                    "text": query_analysis.query,
                    "intent": query_analysis.intent.value,
                    "complexity": query_analysis.complexity.value,
                    "ambiguity": query_analysis.ambiguity.value,
                    "requires_rewrite": (
                        query_analysis.requires_rewrite
                    ),
                    "requires_multi_query": (
                        query_analysis.requires_multi_query
                    ),
                },

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

                    "quality": prompt_pipeline.quality,
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

                "consistency": (
                    consistency_result
                ),

                "answer_quality": (
                    answer_quality_result
                ),

                "pipeline_health": (
                    pipeline_health_result
                ),

                "scorecard": (
                    scorecard_result
                ),

                "citations": (
                    citation_result
                ),

                "grounding": (
                    grounding_result
                ),

                "performance": asdict(performance),
            }



diagnostics_builder = DiagnosticsBuilder()
