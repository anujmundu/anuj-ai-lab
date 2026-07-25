from dataclasses import dataclass

from .models import QueryAnalysis


@dataclass(frozen=True)
class RetrievalStrategy:
    query: str
    k: int
    analysis: QueryAnalysis

    rewrite: bool = False
    expand: bool = False
    multi_query: bool = False