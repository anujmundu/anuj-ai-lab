from __future__ import annotations

import time
from collections.abc import Callable, Iterable

from app.rag.evaluation.answer_evaluator import (
    AnswerEvaluator,
)
from app.rag.evaluation.models import (
    AnswerEvaluationResult,
    BenchmarkResult,
    EvaluationSample,
)
from app.rag.evaluation.retrieval_evaluator import (
    retrieval_evaluator,
)
from app.rag.retrieval_models import RetrievalResult


class BenchmarkService:
    """
    Full end-to-end RAG benchmark orchestration.

    Coordinates:
    - golden evaluation samples
    - RAG execution
    - retrieval evaluation
    - answer evaluation
    - benchmark aggregation

    This service does not implement retrieval, generation,
    hallucination detection, grounding, or citation matching.
    Those responsibilities remain in their existing components.
    """

    def __init__(
        self,
        executor: Callable[
            [EvaluationSample],
            object,
        ],
        answer_evaluator: AnswerEvaluator | None = None,
    ) -> None:

        if not callable(executor):
            raise TypeError(
                "executor must be callable"
            )

        self.executor = executor

        self.answer_evaluator = (
            answer_evaluator
            or AnswerEvaluator()
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _average(
        values: list[float],
    ) -> float:

        if not values:
            return 0.0

        return round(
            sum(values) / len(values),
            4,
        )

    @staticmethod
    def _get(
        result: object,
        key: str,
        default: object = None,
    ) -> object:

        if isinstance(result, dict):
            return result.get(
                key,
                default,
            )

        return getattr(
            result,
            key,
            default,
        )

    @classmethod
    def _retrieval_results(
        cls,
        result: object,
    ) -> list[RetrievalResult]:

        value = cls._get(
            result,
            "retrieval",
            [],
        )

        if value is None:
            return []

        return list(value)

    @classmethod
    def _grounding(
        cls,
        result: object,
    ) -> dict:

        value = cls._get(
            result,
            "grounding",
            {},
        )

        return (
            value
            if isinstance(value, dict)
            else {}
        )

    @classmethod
    def _hallucination(
        cls,
        result: object,
    ) -> dict:

        value = cls._get(
            result,
            "hallucination",
            {},
        )

        return (
            value
            if isinstance(value, dict)
            else {}
        )

    @classmethod
    def _citations(
        cls,
        result: object,
    ) -> dict:

        value = cls._get(
            result,
            "citations",
            {},
        )

        return (
            value
            if isinstance(value, dict)
            else {}
        )

    # --------------------------------------------------
    # Answer aggregation
    # --------------------------------------------------

    @classmethod
    def _aggregate_answers(
        cls,
        results: list[AnswerEvaluationResult],
    ) -> dict:

        if not results:
            return {}

        hallucination_values = [
            result.hallucination_risk
            for result in results
            if result.hallucination_risk is not None
        ]

        return {
            "grounding_score": cls._average(
                [
                    result.grounding_score
                    for result in results
                ]
            ),

            "supported_ratio": cls._average(
                [
                    result.supported_ratio
                    for result in results
                ]
            ),

            "unsupported_ratio": cls._average(
                [
                    result.unsupported_ratio
                    for result in results
                ]
            ),

            "average_confidence": cls._average(
                [
                    result.average_confidence
                    for result in results
                ]
            ),

            "hallucination_risk": cls._average(
                hallucination_values
            ),

            "consistency_score": cls._average(
                [
                    result.consistency_score
                    for result in results
                ]
            ),

            "citation_coverage": cls._average(
                [
                    result.citation_coverage
                    for result in results
                ]
            ),

            "grounded_ratio": cls._average(
                [
                    float(result.grounded)
                    for result in results
                ]
            ),

            "repairable_ratio": cls._average(
                [
                    float(result.repairable)
                    for result in results
                ]
            ),
        }

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def run(
        self,
        samples: Iterable[EvaluationSample],
    ) -> BenchmarkResult:

        start = time.perf_counter()

        sample_list = list(samples)

        retrieval_results = []
        answer_results = []

        for sample in sample_list:

            execution = self.executor(
                sample
            )

            retrieved = self._retrieval_results(
                execution
            )

            retrieval_results.append(
                retrieval_evaluator.evaluate(
                    sample=sample,
                    results=retrieved,
                )
            )

            answer_results.append(
                self.answer_evaluator.evaluate(
                    sample=sample,
                    grounding_result=self._grounding(
                        execution
                    ),
                    hallucination=self._hallucination(
                        execution
                    ),
                    citations=self._citations(
                        execution
                    ),
                )
            )

        elapsed = (
            time.perf_counter()
            - start
        )

        return BenchmarkResult(
            total_samples=len(
                sample_list
            ),

            retrieval=(
                {
                    "hit_at_1": self._average(
                        [
                            result.hit_at_1
                            for result in retrieval_results
                        ]
                    ),
                    "hit_at_3": self._average(
                        [
                            result.hit_at_3
                            for result in retrieval_results
                        ]
                    ),
                    "hit_at_5": self._average(
                        [
                            result.hit_at_5
                            for result in retrieval_results
                        ]
                    ),
                    "hit_at_10": self._average(
                        [
                            result.hit_at_10
                            for result in retrieval_results
                        ]
                    ),
                    "precision_at_1": self._average(
                        [
                            result.precision_at_1
                            for result in retrieval_results
                        ]
                    ),
                    "precision_at_3": self._average(
                        [
                            result.precision_at_3
                            for result in retrieval_results
                        ]
                    ),
                    "precision_at_5": self._average(
                        [
                            result.precision_at_5
                            for result in retrieval_results
                        ]
                    ),
                    "precision_at_10": self._average(
                        [
                            result.precision_at_10
                            for result in retrieval_results
                        ]
                    ),
                    "recall_at_1": self._average(
                        [
                            result.recall_at_1
                            for result in retrieval_results
                        ]
                    ),
                    "recall_at_3": self._average(
                        [
                            result.recall_at_3
                            for result in retrieval_results
                        ]
                    ),
                    "recall_at_5": self._average(
                        [
                            result.recall_at_5
                            for result in retrieval_results
                        ]
                    ),
                    "recall_at_10": self._average(
                        [
                            result.recall_at_10
                            for result in retrieval_results
                        ]
                    ),
                    "reciprocal_rank": self._average(
                        [
                            result.reciprocal_rank
                            for result in retrieval_results
                        ]
                    ),
                    "ndcg_at_5": self._average(
                        [
                            result.ndcg_at_5
                            for result in retrieval_results
                        ]
                    ),
                    "ndcg_at_10": self._average(
                        [
                            result.ndcg_at_10
                            for result in retrieval_results
                        ]
                    ),
                }
                if retrieval_results
                else {}
            ),

            answers=self._aggregate_answers(
                answer_results
            ),

            runtime={
                "total_seconds": round(
                    elapsed,
                    6,
                ),
                "samples_per_second": round(
                    (
                        len(sample_list) / elapsed
                        if elapsed > 0
                        else 0.0
                    ),
                    4,
                ),
                "average_seconds_per_sample": round(
                    (
                        elapsed / len(sample_list)
                        if sample_list
                        else 0.0
                    ),
                    6,
                ),
            },

            metadata={
                "evaluation_type": "full_rag",
                "retrieval_samples": len(
                    retrieval_results
                ),
                "answer_samples": len(
                    answer_results
                ),
            },
        )


benchmark_service = BenchmarkService