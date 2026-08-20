from app.rag.intelligence.dynamic_k import (
    dynamic_k_selector,
)
from app.rag.intelligence.retrieval_strategy import (
    RetrievalStrategy,
)
from app.rag.query.models import QueryAnalysisResult


class RetrievalPlanner:
    """
    Chooses the retrieval strategy.

    The planner receives query analysis produced by the
    retrieval pipeline and converts that analysis into
    an execution strategy.

    It does not analyze the query itself.
    """

    def _should_use_hyde(
        self,
        *,
        analysis: QueryAnalysisResult,
    ) -> bool:

        from app.rag.query.enums import (
            QueryComplexity,
            QueryIntent,
        )

        if analysis.requires_multi_query:
            return False

        if analysis.intent not in {
            QueryIntent.RESEARCH,
            QueryIntent.EXPLANATION,
        }:
            return False

        if analysis.complexity not in {
            QueryComplexity.MEDIUM,
            QueryComplexity.COMPLEX,
        }:
            return False

        return True

    def plan(
        self,
        *,
        query: str,
        k: int,
        analysis: QueryAnalysisResult,
    ) -> RetrievalStrategy:

        dynamic_decision = dynamic_k_selector.select(
            analysis=analysis,
        )

        effective_k = min(
            max(1, k),
            dynamic_decision.k,
        )

        return RetrievalStrategy(
            query=query,
            k=effective_k,
            analysis=analysis,
            rewrite=analysis.requires_rewrite,
            multi_query=analysis.requires_multi_query,
            hyde=self._should_use_hyde(
                analysis=analysis,
            ),
        )


retrieval_planner = RetrievalPlanner()