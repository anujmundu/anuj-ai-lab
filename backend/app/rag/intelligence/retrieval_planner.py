from .retrieval_strategy import RetrievalStrategy


class RetrievalPlanner:
    """
    Chooses the retrieval strategy.

    Initial implementation simply mirrors
    existing behavior.
    """

    def plan(
        self,
        *,
        query: str,
        k: int,
    ) -> RetrievalStrategy:

        return RetrievalStrategy(
            query=query,
            k=k,
        )


retrieval_planner = RetrievalPlanner()