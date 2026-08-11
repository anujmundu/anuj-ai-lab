from dataclasses import dataclass

from app.rag.query.models import QueryAnalysisResult


@dataclass(frozen=True)
class RetrievalStrategy:
    """
    Immutable execution plan produced by the Retrieval Planner.

    This object describes HOW the retrieval pipeline should behave.
    It contains decisions only—it performs no work itself.

    Future capabilities such as query expansion, HyDE,
    multi-query retrieval, metadata filtering, etc.
    will be represented here without changing the pipeline.
    """

    # Query passed to downstream retrieval.
    query: str

    # Number of documents to retrieve.
    k: int

    # Analysis generated from the original query.
    analysis: QueryAnalysisResult

    # Planner decisions.
    rewrite: bool = False
    expand: bool = False
    multi_query: bool = False