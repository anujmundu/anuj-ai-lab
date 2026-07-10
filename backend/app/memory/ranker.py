class MemoryRanker:
    """
    Ranks retrieved memories before they are
    inserted into the prompt.

    Responsibilities

    • Limit prompt memory size
    • Preserve retrieval order
    • Prepare for future ranking strategies

    Future responsibilities

    • Importance weighting
    • Pinned memory boosting
    • Recency weighting
    • Keyword overlap scoring
    • Cross-encoder reranking
    """

    def rank(
        self,
        memories: list,
        limit: int = 5,
    ) -> list:
        """
        Rank retrieved memories.

        The current implementation preserves the
        semantic retrieval order produced by the
        vector search while limiting the number of
        memories sent to the prompt.

        Future versions may reorder memories using
        additional ranking signals.
        """

        if not memories:
            return []

        return memories[:limit]


memory_ranker = MemoryRanker()