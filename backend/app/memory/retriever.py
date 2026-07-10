import re

class MemoryRetriever:
    
    STOP_WORDS = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "am",
        "i",
        "me",
        "my",
        "mine",
        "you",
        "your",
        "yours",
        "he",
        "she",
        "it",
        "they",
        "them",
        "we",
        "our",
        "ours",
        "what",
        "which",
        "who",
        "where",
        "when",
        "why",
        "how",
        "do",
        "does",
        "did",
        "to",
        "of",
        "for",
        "on",
        "in",
        "at",
        "with",
        "and",
        "or",
    }

    def __init__(self, repository):
        self.repository = repository
        
    def _extract_keywords(
        self,
        query: str,
    ) -> list[str]:
        """
        Extract searchable keywords from
        a natural language question.
        """

        normalized = query.lower()

        normalized = re.sub(
            r"[^a-z0-9\s]",
            " ",
            normalized,
        )

        words = normalized.split()

        keywords = []

        for word in words:

            if (
                word
                and word not in self.STOP_WORDS
            ):
                keywords.append(word)

        return keywords

    def relevant(
        self,
        query: str,
    ):
        """
        Retrieve memories that are relevant
        to the supplied query.
        """

        keywords = self._extract_keywords(
            query,
        )

        if not keywords:
            return []

        scored = {}

        for keyword in keywords:

            memories = self.repository.search(
                keyword,
            )

            for memory in memories:

                if memory.id not in scored:

                    scored[memory.id] = {
                        "memory": memory,
                        "score": 0,
                    }

                scored[memory.id]["score"] += 1

        ranked = sorted(
            scored.values(),
            key=lambda item: item["score"],
            reverse=True,
        )

        return [
            item["memory"]
            for item in ranked
        ]

    def recent(self, limit=5):
        return self.repository.get_recent(limit)