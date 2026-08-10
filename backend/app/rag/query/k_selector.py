from __future__ import annotations

from app.rag.query.enums import (
    QueryComplexity,
    QueryIntent,
)


class AdaptiveKSelector:
    """
    Select the retrieval depth based on query analysis.

    This is intentionally deterministic for the initial
    implementation. Future versions can incorporate
    retrieval confidence, corpus statistics, and
    query-specific signals.
    """

    def select(
        self,
        *,
        intent: QueryIntent,
        complexity: QueryComplexity,
        requested_k: int,
    ) -> int:
        """
        Select the effective retrieval K.

        requested_k remains the caller's upper-level preference,
        while query characteristics determine the effective
        retrieval depth.

        The result is always at least 1.
        """

        base_k = max(
            1,
            requested_k,
        )

        if complexity == QueryComplexity.COMPLEX:
            return max(
                base_k,
                8,
            )

        if intent == QueryIntent.RESEARCH:
            return max(
                base_k,
                8,
            )

        if intent == QueryIntent.COMPARISON:
            return max(
                base_k,
                5,
            )

        if intent == QueryIntent.EXPLANATION:
            return max(
                base_k,
                5,
            )

        if complexity == QueryComplexity.MEDIUM:
            return max(
                base_k,
                5,
            )

        return base_k


adaptive_k_selector = AdaptiveKSelector()