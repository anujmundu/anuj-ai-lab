from app.rag.intelligence.dynamic_k import (
    dynamic_k_selector,
)
from app.rag.intelligence.adaptive_retrieval import (
    adaptive_retrieval,
)
from app.rag.intelligence.enums import (
    RetrievalMode,
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
        multi_query: bool,
    ) -> bool:

        from app.rag.query.enums import (
            QueryComplexity,
            QueryIntent,
        )

        if multi_query:
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
        
        adaptive_decision = adaptive_retrieval.decide(
            analysis=analysis,
        )

        effective_k = min(
            max(1, k),
            dynamic_decision.k,
        )
        
        multi_query = (
            adaptive_decision.mode
            == RetrievalMode.MULTI_QUERY
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
            multi_query=multi_query,
            hyde=self._should_use_hyde(
                analysis=analysis,
                multi_query=multi_query,
            ),
            self_query=self_query_applied,
            filters=filters,
            mode=adaptive_decision.mode,
            mode_reason=adaptive_decision.reason,
        )


retrieval_planner = RetrievalPlanner()