from dataclasses import dataclass

from app.rag.query.models import QueryAnalysisResult


@dataclass(frozen=True)
class RetrievalStrategy:
    """
    Immutable execution plan produced by the Retrieval Planner.

    The strategy describes HOW retrieval should behave.
    It performs no retrieval work itself.
    """

    query: str
    k: int
    analysis: QueryAnalysisResult

    rewrite: bool = False
    expand: bool = False
    multi_query: bool = False
    hyde: bool = False