from app.memory.classifier import memory_classifier
from app.memory.schemas import MemoryCreate


class MemoryExtractor:
    """
    Rule-based memory extraction engine.

    Responsibilities:
    - Decide whether a message is worth remembering.
    - Classify the memory.
    - Estimate importance.
    - Produce a MemoryCreate schema.
    """

    QUESTION_PREFIXES = (
        "what",
        "why",
        "how",
        "when",
        "where",
        "who",
        "which",
        "do",
        "does",
        "did",
        "can",
        "could",
        "would",
        "should",
        "is",
        "are",
    )

    def should_extract(
        self,
        text: str,
    ) -> bool:

        text = text.strip()

        normalized = text.lower()

        if (
            text.endswith("?")
            or normalized.startswith(
                self.QUESTION_PREFIXES
            )
        ):
            return False

        if len(text) < 10:
            return False

        category = (
            memory_classifier.classify(
                text,
            )
        )

        return category != "general"

    def importance_score(
        self,
        category: str,
    ) -> int:
        scores = {
            "preferences": 4,
            "career": 5,
            "education": 5,
            "skills": 4,
            "projects": 5,
            "location": 3,
            "general": 1,
        }

        return scores.get(
            category,
            1,
        )

    def extract(
        self,
        text: str,
    ) -> MemoryCreate | None:
        if not self.should_extract(
            text,
        ):
            return None

        category = (
            memory_classifier.classify(
                text,
            )
        )

        importance = (
            self.importance_score(
                category,
            )
        )

        return MemoryCreate(
            content=text,
            category=category,
            importance=importance,
        )


memory_extractor = MemoryExtractor()