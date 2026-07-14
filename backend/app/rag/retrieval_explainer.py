from app.rag.retrieval_explainer_config import (
    RetrievalExplainerConfig,
)


class RetrievalExplainer:
    """
    Generates human-readable explanations
    describing why a document was retrieved.

    Purely diagnostic.

    Does not modify retrieval.
    """

    def __init__(
        self,
        config: RetrievalExplainerConfig | None = None,
    ):

        self.config = (
            config
            or RetrievalExplainerConfig()
        )

    def explain(
        self,
        retrieval: dict,
    ) -> list[str]:

        if not self.config.enabled:

            return []

        reasons = []

        semantic = retrieval["semantic_score"]

        keyword = retrieval["keyword_score"] or 0.0

        combined = retrieval["combined_score"]

        if semantic >= self.config.semantic_high:

            reasons.append(
                "High semantic similarity"
            )

        elif semantic >= self.config.semantic_medium:

            reasons.append(
                "Moderate semantic similarity"
            )

        if keyword >= self.config.keyword_high:

            reasons.append(
                "Strong keyword overlap"
            )

        elif keyword > 0:

            reasons.append(
                "Keyword overlap"
            )

        if combined >= self.config.combined_high:

            reasons.append(
                "High combined retrieval score"
            )

        if retrieval.get(
            "semantic_rank"
        ) == 1:

            reasons.append(
                "Top semantic result"
            )

        if retrieval.get(
            "keyword_rank"
        ) == 1:

            reasons.append(
                "Top keyword result"
            )

        if not reasons:

            reasons.append(
                "Selected after hybrid retrieval"
            )

        return reasons


retrieval_explainer = RetrievalExplainer()