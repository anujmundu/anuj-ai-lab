from app.rag.embedding_similarity_config import (
    EmbeddingSimilarityConfig,
)

from app.rag.semantic_matcher import (
    semantic_matcher,
)


class EmbeddingSimilarity:
    """
    Semantic similarity abstraction.

    Responsibilities

    • Compare two texts semantically
    • Normalize similarity output
    • Provide confidence estimation

    Current backend

    • SemanticMatcher

    Future backends

    • SentenceTransformer
    • OpenAI Embeddings
    • BGE
    • E5

    Consumers should never call
    SemanticMatcher directly.
    """

    def __init__(
        self,
        config: EmbeddingSimilarityConfig | None = None,
    ):

        self.config = (
            config
            or EmbeddingSimilarityConfig()
        )

    # --------------------------------------------------

    def compare(
        self,
        text_a: str,
        text_b: str,
    ) -> dict:

        if not self.config.enabled:

            return {}

        similarity = (
            semantic_matcher.compare(
                text_a,
                text_b,
            )
        )

        metrics = similarity.get(
            "metrics",
            {},
        )

        score = metrics.get(
            "overall",
            0.0,
        )

        if score >= self.config.high_similarity:

            level = "High"

        elif score >= self.config.medium_similarity:

            level = "Medium"

        elif score >= self.config.low_similarity:

            level = "Low"

        else:

            level = "Very Low"

        return {

            "similarity": score,

            "confidence": {

                "score": score,

                "level": level,
            },

            "metrics": (
                similarity["metrics"]
                if self.config.include_similarity_breakdown
                else {}
            ),

            "diagnostics": (
                similarity["diagnostics"]
                if self.config.include_diagnostics
                else {}
            ),

            "explanation": similarity[
                "explanation"
            ],
        }


embedding_similarity = (
    EmbeddingSimilarity()
)