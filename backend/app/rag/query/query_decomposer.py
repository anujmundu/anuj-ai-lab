from __future__ import annotations

from dataclasses import dataclass

from app.rag.query.enums import QueryComplexity
from app.rag.query.models import QueryAnalysisResult


@dataclass(frozen=True, slots=True)
class QueryDecompositionResult:
    original_query: str
    sub_queries: list[str]
    decomposed: bool
    reason: str


class QueryDecomposer:
    """
    Deterministic query decomposition layer.

    This component decides whether a complex query should be
    separated into smaller retrieval queries.

    It does not:
        - perform retrieval
        - call an LLM
        - generate embeddings
        - modify the original query
    """

    def decompose(
        self,
        query: str,
        analysis: QueryAnalysisResult,
    ) -> QueryDecompositionResult:

        normalized = query.strip()

        if not normalized:
            return QueryDecompositionResult(
                original_query=normalized,
                sub_queries=[],
                decomposed=False,
                reason="empty_query",
            )

        if analysis.complexity != QueryComplexity.COMPLEX:
            return QueryDecompositionResult(
                original_query=normalized,
                sub_queries=[],
                decomposed=False,
                reason="query_not_complex",
            )

        sub_queries = self._build_sub_queries(
            normalized,
        )

        if not sub_queries:
            return QueryDecompositionResult(
                original_query=normalized,
                sub_queries=[],
                decomposed=False,
                reason="no_decomposition_pattern",
            )

        return QueryDecompositionResult(
            original_query=normalized,
            sub_queries=sub_queries,
            decomposed=True,
            reason="complex_query",
        )

    def _build_sub_queries(
        self,
        query: str,
    ) -> list[str]:

        queries: list[str] = []

        queries.append(query)

        lowered = query.lower()

        markers = [
            " including ",
            " including:",
            " and ",
        ]

        for marker in markers:

            if marker not in lowered:
                continue

            index = lowered.find(marker)

            base = query[:index].strip()
            remainder = query[
                index + len(marker):
            ].strip()

            if not base or not remainder:
                continue

            parts = [
                part.strip(" .,;:")
                for part in remainder.split(",")
            ]

            for part in parts:

                if not part:
                    continue

                queries.append(
                    f"{base} {part}"
                )

            break

        return self._deduplicate(queries)

    @staticmethod
    def _deduplicate(
        queries: list[str],
    ) -> list[str]:

        seen: set[str] = set()
        result: list[str] = []

        for query in queries:

            normalized = query.strip()

            if not normalized:
                continue

            key = normalized.casefold()

            if key in seen:
                continue

            seen.add(key)
            result.append(normalized)

        return result


query_decomposer = QueryDecomposer()