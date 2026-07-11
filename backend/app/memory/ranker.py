class MemoryRanker:
    """
    Lightweight ranking for retrieved memories.

    Higher importance memories are preferred.

    Pinned memories receive an additional bonus.
    """

    PINNED_BONUS = 10

    def rank(
        self,
        memories,
    ):
        """
        Rank memories using deterministic scoring.
        """
        
        if not memories:
            return []

        scored = []

        for memory in memories:

            score = memory.importance

            if memory.pinned:
                score += self.PINNED_BONUS

            scored.append(
                (
                    score,
                    memory,
                )
            )

        scored.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        return [
            memory
            for _, memory in scored
        ]


memory_ranker = MemoryRanker()