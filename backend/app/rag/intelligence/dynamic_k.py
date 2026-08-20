from __future__ import annotations

from dataclasses import dataclass

from app.rag.query.enums import (
    QueryAmbiguity,
    QueryComplexity,
    QueryIntent,
)
from app.rag.query.models import QueryAnalysisResult


@dataclass(frozen=True)
class DynamicKDecision:
    k: int
    reason: str


class DynamicKSelector:
    """
    Selects the retrieval depth from query characteristics.

    This component only decides K.
    It does not execute retrieval.
    """

    MIN_K = 3
    DEFAULT_K = 5
    MAX_K = 12

    def select(
        self,
        *,
        analysis: QueryAnalysisResult,
    ) -> DynamicKDecision:

        if analysis.complexity == QueryComplexity.COMPLEX:
            k = 10
            reason = "complex_query"

        elif analysis.complexity == QueryComplexity.MEDIUM:
            k = 7
            reason = "medium_complexity_query"

        else:
            k = self.DEFAULT_K
            reason = "simple_query"

        if analysis.ambiguity == QueryAmbiguity.HIGH:
            k += 2
            reason = "high_ambiguity_query"

        elif analysis.ambiguity == QueryAmbiguity.MEDIUM:
            k += 1

        if analysis.intent in {
            QueryIntent.RESEARCH,
            QueryIntent.COMPARISON,
        }:
            k += 2
            reason = "broad_information_need"

        k = max(self.MIN_K, min(self.MAX_K, k))

        return DynamicKDecision(
            k=k,
            reason=reason,
        )


dynamic_k_selector = DynamicKSelector()