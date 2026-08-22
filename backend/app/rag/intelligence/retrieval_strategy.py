from dataclasses import dataclass, field

from app.rag.query.models import QueryAnalysisResult


@dataclass(frozen=True)
class RetrievalStrategy:
    """
    Immutable execution plan produced by the Retrieval Planner.

    The strategy describes HOW retrieval should behave.
    It performs no retrieval work itself.

    Self-query parsing may extract structured metadata
    constraints from the query. When constraints are found,
    ``query`` contains the normalized semantic query and
    ``self_query`` is True.

    When no constraints are found, the original query is
    preserved exactly.
    """

    query: str
    k: int
    analysis: QueryAnalysisResult

    rewrite: bool = False
    expand: bool = False
    multi_query: bool = False
    hyde: bool = False

    # Whether self-query metadata extraction was applied.
    self_query: bool = False

    # Structured metadata constraints extracted from the query.
    filters: dict[str, str] = field(
        default_factory=dict,
    )