from .query_analyzer import query_analyzer
from .retrieval_strategy import RetrievalStrategy


class RetrievalPlanner:
    """
    Chooses the retrieval strategy.

    Initial implementation performs lightweight
    query analysis and selects an adaptive top-k.
    """

    def plan(
        self,
        *,
        query: str,
        k: int,
    ) -> RetrievalStrategy:

        analysis = query_analyzer.analyze(query)

        if analysis.word_count <= 5:
            adaptive_k = 3
        elif analysis.word_count <= 12:
            adaptive_k = 5
        else:
            adaptive_k = 8

        return RetrievalStrategy(
            query=query,
            k=adaptive_k,
            analysis=analysis,
        )


retrieval_planner = RetrievalPlanner()