from app.rag.query.models import QueryAnalysisResult
from app.rag.query.k_selector import adaptive_k_selector
from .retrieval_strategy import RetrievalStrategy


class RetrievalPlanner:
    """
    Chooses the retrieval strategy.

    The planner receives query analysis produced by the
    retrieval pipeline and converts that analysis into
    an execution strategy.

    It does not analyze the query itself.
    """

    def plan(
        self,
        *,
        query: str,
        k: int,
        analysis: QueryAnalysisResult,
    ) -> RetrievalStrategy:

        effective_k = adaptive_k_selector.select(
            intent=analysis.intent,
            complexity=analysis.complexity,
            requested_k=k,
        )

        return RetrievalStrategy(
            query=query,
            k=effective_k,
            analysis=analysis,
            rewrite=analysis.requires_rewrite,
            multi_query=analysis.requires_multi_query,
        )


retrieval_planner = RetrievalPlanner()