from __future__ import annotations

import time
from collections.abc import Callable, Iterable

from app.rag.evaluation.models import (
    BenchmarkResult,
    EvaluationSample,
    RetrievalEvaluationResult,
)
from app.rag.evaluation.retrieval_evaluator import (
    retrieval_evaluator,
)
from app.rag.retrieval_models import RetrievalResult


class BenchmarkRunner:
    """
    Executes golden-dataset evaluation samples and aggregates
    retrieval benchmark results.

    The runner is orchestration-only.

    It does not:
    - modify retrieval behavior
    - modify generation behavior
    - access ChromaDB directly
    - implement retrieval metrics itself

    Retrieval execution is injected through `executor`.
    """

    def __init__(
        self,
        executor: Callable[
            [EvaluationSample],
            Iterable[RetrievalResult],
        ],
    ) -> None:

        if not callable(executor):
            raise TypeError(
                "executor must be callable"
            )

        self.executor = executor

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
    def _aggregate_retrieval(
        results: list[RetrievalEvaluationResult],
    ) -> dict:

        if not results:
            return {}

        return {

            "hit_at_1": BenchmarkRunner._average(
                [
                    result.hit_at_1
                    for result in results
                ]
            ),

            "hit_at_3": BenchmarkRunner._average(
                [
                    result.hit_at_3
                    for result in results
                ]
            ),

            "hit_at_5": BenchmarkRunner._average(
                [
                    result.hit_at_5
                    for result in results
                ]
            ),

            "hit_at_10": BenchmarkRunner._average(
                [
                    result.hit_at_10
                    for result in results
                ]
            ),

            "precision_at_1": BenchmarkRunner._average(
                [
                    result.precision_at_1
                    for result in results
                ]
            ),

            "precision_at_3": BenchmarkRunner._average(
                [
                    result.precision_at_3
                    for result in results
                ]
            ),

            "precision_at_5": BenchmarkRunner._average(
                [
                    result.precision_at_5
                    for result in results
                ]
            ),

            "precision_at_10": BenchmarkRunner._average(
                [
                    result.precision_at_10
                    for result in results
                ]
            ),

            "recall_at_1": BenchmarkRunner._average(
                [
                    result.recall_at_1
                    for result in results
                ]
            ),

            "recall_at_3": BenchmarkRunner._average(
                [
                    result.recall_at_3
                    for result in results
                ]
            ),

            "recall_at_5": BenchmarkRunner._average(
                [
                    result.recall_at_5
                    for result in results
                ]
            ),

            "recall_at_10": BenchmarkRunner._average(
                [
                    result.recall_at_10
                    for result in results
                ]
            ),

            "reciprocal_rank": BenchmarkRunner._average(
                [
                    result.reciprocal_rank
                    for result in results
                ]
            ),

            "ndcg_at_5": BenchmarkRunner._average(
                [
                    result.ndcg_at_5
                    for result in results
                ]
            ),

            "ndcg_at_10": BenchmarkRunner._average(
                [
                    result.ndcg_at_10
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
        """
        Execute the benchmark over the supplied samples.
        """

        start = time.perf_counter()

        sample_list = list(samples)

        retrieval_results: list[
            RetrievalEvaluationResult
        ] = []

        for sample in sample_list:

            retrieved = list(
                self.executor(sample)
            )

            evaluation = (
                retrieval_evaluator.evaluate(
                    sample=sample,
                    results=retrieved,
                )
            )

            retrieval_results.append(
                evaluation
            )

        elapsed = (
            time.perf_counter()
            - start
        )

        return BenchmarkResult(
            total_samples=len(
                sample_list
            ),

            retrieval=self._aggregate_retrieval(
                retrieval_results
            ),

            answers={},

            runtime={
                "total_seconds": round(
                    elapsed,
                    6,
                ),

                "samples_per_second": round(
                    (
                        len(sample_list)
                        / elapsed
                        if elapsed > 0
                        else 0.0
                    ),
                    4,
                ),
            },

            metadata={
                "evaluation_type": "retrieval",
            },
        )


benchmark_runner = BenchmarkRunner