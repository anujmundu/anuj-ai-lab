from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.intelligence.retrieval_planner import retrieval_planner
from app.rag.query.models import QueryAnalysisResult


class RetrievalIntelligence:
    """
    Entry point for all retrieval operations.

    Receives query analysis from the retrieval pipeline
    and delegates retrieval planning to RetrievalPlanner.

    The selected retrieval strategy is preserved in the
    result so downstream diagnostics can distinguish
    requested K from effective K.
    """

    def retrieve(
        self,
        *,
        query: str,
        k: int,
        analysis: QueryAnalysisResult,
        profiler=None,
    ):
        strategy = retrieval_planner.plan(
            query=query,
            k=k,
            analysis=analysis,
        )

        results = hybrid_retriever.retrieve(
            query=strategy.query,
            k=strategy.k,
            profiler=profiler,
        )

        # Preserve the planner decision for downstream
        # diagnostics and pipeline observability.
        results["strategy"] = strategy
        results["effective_k"] = strategy.k

        return results


retrieval_intelligence = RetrievalIntelligence()