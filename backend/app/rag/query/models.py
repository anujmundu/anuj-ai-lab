from dataclasses import dataclass

from .enums import (
    QueryAmbiguity,
    QueryComplexity,
    QueryIntent,
)


@dataclass(slots=True)
class QueryAnalysisResult:

    query: str

    intent: QueryIntent

    complexity: QueryComplexity

    ambiguity: QueryAmbiguity

    requires_rewrite: bool

    requires_multi_query: bool