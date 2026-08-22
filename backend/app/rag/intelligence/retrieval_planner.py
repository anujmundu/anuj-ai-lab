from app.rag.intelligence.dynamic_k import (
    dynamic_k_selector,
)
from app.rag.intelligence.retrieval_strategy import (
    RetrievalStrategy,
)
from app.rag.intelligence.self_query import (
    self_query_retriever,
)
from app.rag.query.models import QueryAnalysisResult


class RetrievalPlanner:
    """
    Chooses the retrieval strategy.

    The planner receives query analysis produced by the
    retrieval pipeline and converts that analysis into
    an immutable execution strategy.

    It does not execute retrieval itself.

    Responsibilities:

        1. Determine effective retrieval depth.
        2. Determine whether HyDE should be used.
        3. Determine whether multi-query retrieval is required.
        4. Parse supported metadata constraints from the query.
        5. Preserve the original query when no metadata
           constraints are detected.
        6. Use the normalized semantic query when
           self-query metadata is extracted.
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

        self_query_result = self_query_retriever.parse(
            query,
        )

        filters = dict(
            self_query_result.filters,
        )

        self_query_applied = bool(filters)

        if self_query_applied:
            planned_query = self_query_result.query
        else:
            planned_query = query

        return RetrievalStrategy(
            query=planned_query,
            k=effective_k,
            analysis=analysis,
            rewrite=analysis.requires_rewrite,
            multi_query=analysis.requires_multi_query,
            hyde=self._should_use_hyde(
                analysis=analysis,
            ),
            self_query=self_query_applied,
            filters=filters,
        )


retrieval_planner = RetrievalPlanner()