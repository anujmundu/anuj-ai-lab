from app.memory.rules import MEMORY_RULES


class MemoryClassifier:
    def classify(
        self,
        text: str,
    ) -> str:
        """
        Determine the most appropriate memory category
        for the supplied text.

        Returns:
            str: category name
        """

        normalized = text.lower()

        best_category = "general"
        best_score = 0

        for (
            category,
            keywords,
        ) in MEMORY_RULES.items():

            score = sum(
                keyword in normalized
                for keyword in keywords
            )

            if score > best_score:
                best_score = score
                best_category = category

        return best_category


memory_classifier = MemoryClassifier()