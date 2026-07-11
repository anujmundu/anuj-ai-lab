from datetime import datetime


class MemoryRanker:
    """
    Rank retrieved memories before they are added
    to the prompt.

    Current ranking signals

    • Importance
    • Recency
    • Pinned status

    Future ranking signals

    • Keyword overlap
    • Semantic similarity
    • User feedback
    • Cross-encoder reranking
    """

    PINNED_BONUS = 10

    RECENT_MEMORY_DAYS = 7

    RECENT_BONUS = 3

    OLDER_BONUS = 1

    def recency_bonus(
        self,
        memory,
    ) -> int:
        """
        Compute the recency contribution
        for a memory.
        """

        now = datetime.now()

        age = (
            now
            - memory.created_at.replace(
                tzinfo=None,
            )
        ).days

        if age <= self.RECENT_MEMORY_DAYS:
            return self.RECENT_BONUS

        return self.OLDER_BONUS

    def rank(
        self,
        memories,
    ):
        """
        Rank memories using deterministic scoring.
        """

        scored = []

        for memory in memories:

            recency = self.recency_bonus(
                memory,
            )

            pinned_bonus = (
                self.PINNED_BONUS
                if memory.pinned
                else 0
            )

            score = 0

            score += memory.importance

            score += recency

            score += pinned_bonus

            scored.append(
                {
                    "memory": memory,
                    "importance": memory.importance,
                    "recency": recency,
                    "pinned": pinned_bonus,
                    "score": score,
                }
            )

        scored.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return [
            item["memory"]
            for item in scored
        ]


memory_ranker = MemoryRanker()