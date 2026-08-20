from app.rag.intelligence.dynamic_k import (
    DynamicKSelector,
)
from app.rag.query.models import QueryAnalysisResult

from .retrieval_strategy import RetrievalStrategy


class RetrievalPlanner:
    """
    Chooses the retrieval strategy and retrieval depth.

    The planner receives query analysis produced by the
    retrieval pipeline and converts that analysis into
    an execution strategy.

    It does not analyze or execute the query itself.
    """

    def __init__(
        self,
        *,
        dynamic_k_selector: DynamicKSelector | None = None,
    ) -> None:

        self.dynamic_k_selector = (
            dynamic_k_selector
            or DynamicKSelector()
        )

    def plan(
        self,
        *,
        query: str,
        k: int,
        analysis: QueryAnalysisResult,
    ) -> RetrievalStrategy:

        decision = self.dynamic_k_selector.select(
            analysis=analysis,
        )

        effective_k = max(
            1,
            min(k, decision.k),
        )

        return RetrievalStrategy(
            query=query,
            k=effective_k,
            analysis=analysis,
            rewrite=analysis.requires_rewrite,
            multi_query=analysis.requires_multi_query,
        )


retrieval_planner = RetrievalPlanner()