from __future__ import annotations

import math

from app.rag.evaluation.models import (
    EvaluationSample,
    RetrievalEvaluationResult,
)
from app.rag.retrieval_models import RetrievalResult


class RetrievalEvaluator:
    """
    Evaluates ranked retrieval results against golden
    ground-truth chunks.

    This component is diagnostic/evaluation-only and never
    changes retrieval behavior.
    """

    @staticmethod
    def _identity(
        result: RetrievalResult,
    ) -> tuple[str, str]:
        return (
            result.filename,
            result.chunk_id,
        )

    @staticmethod
    def _relevant_identities(
        sample: EvaluationSample,
    ) -> set[tuple[str, str]]:
        return {
            (
                chunk.filename,
                chunk.chunk_id,
            )
            for chunk in sample.relevant_chunks
        }

    @classmethod
    def _hits(
        cls,
        results: list[RetrievalResult],
        relevant: set[tuple[str, str]],
        k: int,
    ) -> int:
        return int(
            any(
                cls._identity(result) in relevant
                for result in results[:k]
            )
        )

    @classmethod
    def _precision(
        cls,
        results: list[RetrievalResult],
        relevant: set[tuple[str, str]],
        k: int,
    ) -> float:
        if k <= 0:
            return 0.0

        retrieved = results[:k]

        if not retrieved:
            return 0.0

        relevant_count = sum(
            cls._identity(result) in relevant
            for result in retrieved
        )

        return relevant_count / len(retrieved)

    @classmethod
    def _recall(
        cls,
        results: list[RetrievalResult],
        relevant: set[tuple[str, str]],
        k: int,
    ) -> float:
        if not relevant:
            return 0.0

        retrieved = results[:k]

        relevant_count = sum(
            cls._identity(result) in relevant
            for result in retrieved
        )

        return relevant_count / len(relevant)

    @classmethod
    def _reciprocal_rank(
        cls,
        results: list[RetrievalResult],
        relevant: set[tuple[str, str]],
    ) -> float:
        for rank, result in enumerate(results, start=1):
            if cls._identity(result) in relevant:
                return 1.0 / rank

        return 0.0

    @classmethod
    def _ndcg(
        cls,
        results: list[RetrievalResult],
        relevant: set[tuple[str, str]],
        k: int,
    ) -> float:
        if not relevant or k <= 0:
            return 0.0

        retrieved = results[:k]

        dcg = 0.0

        for rank, result in enumerate(
            retrieved,
            start=1,
        ):
            relevance = int(
                cls._identity(result) in relevant
            )

            if relevance:
                dcg += relevance / math.log2(rank + 1)

        ideal_relevant = min(
            len(relevant),
            k,
        )

        if ideal_relevant == 0:
            return 0.0

        idcg = sum(
            1.0 / math.log2(rank + 1)
            for rank in range(
                1,
                ideal_relevant + 1,
            )
        )

        return dcg / idcg

    def evaluate(
        self,
        *,
        sample: EvaluationSample,
        results: list[RetrievalResult],
    ) -> RetrievalEvaluationResult:
        """
        Evaluate one ranked retrieval result list.
        """

        relevant = self._relevant_identities(
            sample,
        )

        return RetrievalEvaluationResult(
            sample_id=sample.sample_id,

            hit_at_1=self._hits(
                results,
                relevant,
                1,
            ),

            hit_at_3=self._hits(
                results,
                relevant,
                3,
            ),

            hit_at_5=self._hits(
                results,
                relevant,
                5,
            ),

            hit_at_10=self._hits(
                results,
                relevant,
                10,
            ),

            precision_at_1=self._precision(
                results,
                relevant,
                1,
            ),

            precision_at_3=self._precision(
                results,
                relevant,
                3,
            ),

            precision_at_5=self._precision(
                results,
                relevant,
                5,
            ),

            precision_at_10=self._precision(
                results,
                relevant,
                10,
            ),

            recall_at_1=self._recall(
                results,
                relevant,
                1,
            ),

            recall_at_3=self._recall(
                results,
                relevant,
                3,
            ),

            recall_at_5=self._recall(
                results,
                relevant,
                5,
            ),

            recall_at_10=self._recall(
                results,
                relevant,
                10,
            ),

            reciprocal_rank=self._reciprocal_rank(
                results,
                relevant,
            ),

            ndcg_at_5=self._ndcg(
                results,
                relevant,
                5,
            ),

            ndcg_at_10=self._ndcg(
                results,
                relevant,
                10,
            ),
        )


retrieval_evaluator = RetrievalEvaluator()