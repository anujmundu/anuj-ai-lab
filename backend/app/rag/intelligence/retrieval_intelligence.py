from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.intelligence.retrieval_planner import retrieval_planner

from .models import RetrievalRequest


class RetrievalIntelligence:
    """
    Entry point for all retrieval operations.

    Stage 5 begins as a transparent wrapper around the
    existing HybridRetriever.

    Future versions will introduce query analysis,
    planning and adaptive retrieval while preserving
    this public interface.
    """

    def retrieve(
        self,
        *,
        query: str,
        k: int,
        profiler=None,
    ):

        request = RetrievalRequest(
            query=query,
            k=k,
        )

        strategy = retrieval_planner.plan(
            query=query,
            k=k,
        )

        return hybrid_retriever.retrieve(
            query=strategy.query,
            k=strategy.k,
            profiler=profiler,
        )


retrieval_intelligence = RetrievalIntelligence()