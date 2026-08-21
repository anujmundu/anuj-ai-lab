from dataclasses import dataclass, field

from app.rag.query.models import QueryAnalysisResult


@dataclass(frozen=True)
class RetrievalStrategy:
    """
    Immutable execution plan produced by the Retrieval Planner.

    The strategy describes HOW retrieval should behave.
    It performs no retrieval work itself.

    Self-query information is carried as structured metadata
    so downstream components can decide how to apply filters.
    """

    query: str
    k: int
    analysis: QueryAnalysisResult

    rewrite: bool = False
    expand: bool = False
    multi_query: bool = False
    hyde: bool = False

    self_query: bool = False

    filters: dict[str, str] = field(
        default_factory=dict,
    )