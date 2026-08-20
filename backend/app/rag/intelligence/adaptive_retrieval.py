from __future__ import annotations

from dataclasses import dataclass

from app.rag.intelligence.enums import RetrievalMode
from app.rag.query.enums import (
    QueryAmbiguity,
    QueryComplexity,
    QueryIntent,
)
from app.rag.query.models import QueryAnalysisResult


@dataclass(frozen=True)
class AdaptiveRetrievalDecision:
    """
    Deterministic retrieval decision produced from query analysis.

    This component decides retrieval strategy only.
    It does not execute retrieval.
    """

    mode: RetrievalMode
    reason: str


class AdaptiveRetrieval:
    """
    Selects an appropriate retrieval mode from query characteristics.

    The current policy is deterministic and intentionally small.
    It provides the decision boundary for future adaptive signals.
    """

    def decide(
        self,
        *,
        analysis: QueryAnalysisResult,
    ) -> AdaptiveRetrievalDecision:

        if analysis.requires_multi_query:
            return AdaptiveRetrievalDecision(
                mode=RetrievalMode.MULTI_QUERY,
                reason="query_analysis_requires_multi_query",
            )

        if (
            analysis.complexity == QueryComplexity.COMPLEX
            and analysis.intent == QueryIntent.RESEARCH
        ):
            return AdaptiveRetrievalDecision(
                mode=RetrievalMode.MULTI_QUERY,
                reason="complex_research_query",
            )

        if analysis.ambiguity == QueryAmbiguity.HIGH:
            return AdaptiveRetrievalDecision(
                mode=RetrievalMode.STANDARD,
                reason="high_ambiguity_requires_rewrite_or_analysis",
            )

        return AdaptiveRetrievalDecision(
            mode=RetrievalMode.STANDARD,
            reason="standard_query",
        )


adaptive_retrieval = AdaptiveRetrieval()