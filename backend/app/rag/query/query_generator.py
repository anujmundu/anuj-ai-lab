from __future__ import annotations

from app.rag.query.models import QueryAnalysisResult
from app.rag.query.enums import QueryIntent


class QueryGenerator:
    """
    Deterministically generates alternative retrieval queries.

    The initial implementation intentionally avoids LLM calls.

    Future implementations may support:
    - LLM-based query expansion
    - semantic rewriting
    - HyDE
    - domain-aware expansion
    """

    def generate(
        self,
        *,
        query: str,
        analysis: QueryAnalysisResult,
    ) -> list[str]:

        normalized_query = query.strip()

        if not normalized_query:
            return []

        queries = [
            normalized_query,
        ]

        if analysis.intent == QueryIntent.COMPARISON:

            queries.extend(
                [
                    f"{normalized_query} comparison",
                    f"differences between {normalized_query}",
                ]
            )

        elif analysis.intent == QueryIntent.RESEARCH:

            queries.extend(
                [
                    f"{normalized_query} overview",
                    f"{normalized_query} key concepts",
                ]
            )

        elif analysis.intent == QueryIntent.EXPLANATION:

            queries.extend(
                [
                    f"{normalized_query} explanation",
                    f"{normalized_query} fundamentals",
                ]
            )

        else:

            queries.extend(
                [
                    f"{normalized_query} overview",
                    f"{normalized_query} details",
                ]
            )

        # Remove duplicates while preserving order.
        unique_queries = list(
            dict.fromkeys(
                query.strip()
                for query in queries
                if query.strip()
            )
        )

        return unique_queries


query_generator = QueryGenerator()
