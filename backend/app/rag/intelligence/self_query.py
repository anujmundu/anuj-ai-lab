from __future__ import annotations

import re

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SelfQueryResult:
    """
    Structured representation of a natural-language retrieval query.

    The semantic query is preserved for downstream retrieval while
    explicitly recognized metadata constraints are extracted into
    structured filters.

    This component performs parsing only.

    It does not:
        - execute retrieval
        - access the vector store
        - access the database
        - call an LLM
        - modify the original query
    """

    query: str
    filters: dict[str, str]


class SelfQueryRetriever:
    """
    Deterministic self-query parser.

    The initial implementation recognizes a small, controlled
    metadata vocabulary:

        source
        filename
        document_type
        mime_type
        asset_id

    Metadata constraints are written using natural-language
    patterns such as:

        from research.pdf
        source research.pdf
        filename report.pdf
        document type pdf
        mime type application/pdf
        asset asset-123

    Unrecognized text remains part of the semantic query.
    """

    _FILTER_PATTERNS: tuple[
        tuple[str, tuple[str, ...]],
        ...
    ] = (
        (
            "source",
            (
                r"\bfrom\s+([^\s,]+)",
                r"\bsource\s*[:=]?\s*([^\s,]+)",
            ),
        ),
        (
            "filename",
            (
                r"\bfilename\s*[:=]?\s*([^\s,]+)",
                r"\bfile\s+name\s*[:=]?\s*([^\s,]+)",
            ),
        ),
        (
            "document_type",
            (
                r"\bdocument\s+type\s*[:=]?\s*([^\s,]+)",
                r"\bdoc(?:ument)?\s+type\s*[:=]?\s*([^\s,]+)",
            ),
        ),
        (
            "mime_type",
            (
                r"\bmime\s+type\s*[:=]?\s*([^\s,]+)",
                r"\bmime\s*[:=]\s*([^\s,]+)",
            ),
        ),
        (
            "asset_id",
            (
                r"\basset\s+id\s*[:=]?\s*([^\s,]+)",
                r"\basset\s*[:=]\s*([^\s,]+)",
            ),
        ),
    )

    def parse(
        self,
        query: str,
    ) -> SelfQueryResult:

        if not query or not query.strip():
            return SelfQueryResult(
                query="",
                filters={},
            )

        semantic_query = query.strip()
        filters: dict[str, str] = {}

        for field, patterns in self._FILTER_PATTERNS:

            for pattern in patterns:

                match = re.search(
                    pattern,
                    semantic_query,
                    flags=re.IGNORECASE,
                )

                if match is None:
                    continue

                value = match.group(1).strip()

                if not value:
                    continue

                filters[field] = value

                semantic_query = (
                    semantic_query[: match.start()]
                    + " "
                    + semantic_query[match.end() :]
                )

                break

        semantic_query = self._normalize_query(
            semantic_query
        )

        return SelfQueryResult(
            query=semantic_query,
            filters=filters,
        )

    @staticmethod
    def _normalize_query(
        query: str,
    ) -> str:

        query = re.sub(
            r"\s+",
            " ",
            query,
        )

        return query.strip()


self_query_retriever = SelfQueryRetriever()