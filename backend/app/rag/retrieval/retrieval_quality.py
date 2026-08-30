from statistics import variance

from app.rag.retrieval_quality_config import (
    RetrievalQualityConfig,
)


class RetrievalQuality:
    """
    Estimates the quality of retrieved documents.

    This component is diagnostics-only.

    It never changes retrieval results.

    Current metrics

    • Coverage
    • Redundancy
    • Diversity
    • Semantic Spread
    • Overall Quality

    Future metrics

    • Cross-encoder gain
    • Query coverage
    • Recall estimate
    • Chunk utilization
    • Retrieval entropy
    • Parent document coverage
    """

    def __init__(
        self,
        config: RetrievalQualityConfig | None = None,
    ):

        self.config = (
            config
            or RetrievalQualityConfig()
        )

    # --------------------------------------------------
    # Coverage
    # --------------------------------------------------

    def _coverage(
        self,
        retrieval: list[dict],
    ) -> float:

        if not retrieval:
            return 0.0

        scores = [
            item["combined_score"]
            for item in retrieval
        ]

        return sum(scores) / len(scores)

    # --------------------------------------------------
    # Redundancy
    # --------------------------------------------------

    def _redundancy(
        self,
        metadatas: list[dict],
    ) -> float:

        if len(metadatas) <= 1:
            return 0.0

        duplicate_pairs = 0

        comparisons = 0

        for i in range(len(metadatas)):

            for j in range(i + 1, len(metadatas)):

                comparisons += 1

                same_document = (

                    metadatas[i]["filename"]
                    == metadatas[j]["filename"]

                )

                nearby_chunks = (

                    abs(
                        metadatas[i]["chunk_number"]
                        - metadatas[j]["chunk_number"]
                    )

                    <= self.config.nearby_chunk_distance

                )

                if same_document and nearby_chunks:

                    duplicate_pairs += 1

        if comparisons == 0:
            return 0.0

        return duplicate_pairs / comparisons

    # --------------------------------------------------
    # Diversity
    # --------------------------------------------------

    def _diversity(
        self,
        redundancy: float,
    ) -> float:

        return max(
            0.0,
            1.0 - redundancy,
        )

    # --------------------------------------------------
    # Semantic Spread
    # --------------------------------------------------

    def _semantic_spread(
        self,
        retrieval: list[dict],
    ) -> float:

        if len(retrieval) <= 1:
            return 1.0

        scores = [

            item["combined_score"]

            for item in retrieval

        ]

        try:

            spread = 1.0 - variance(scores)

        except Exception:

            spread = 1.0

        return max(
            0.0,
            min(1.0, spread),
        )

    # --------------------------------------------------
    # Overall Quality
    # --------------------------------------------------

    def _overall_quality(
        self,
        coverage: float,
        diversity: float,
        spread: float,
    ) -> str:

        if (

            coverage
            >= self.config.excellent_coverage

            and diversity >= 0.60

            and spread >= 0.60

        ):

            return "Excellent"

        if coverage >= self.config.good_coverage:

            return "Good"

        if coverage >= self.config.fair_coverage:

            return "Fair"

        return "Poor"

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def evaluate(
        self,
        *,
        retrieval: list[dict],
        metadatas: list[dict],
    ) -> dict:

        if not self.config.enabled:

            return {}

        coverage = self._coverage(
            retrieval,
        )

        redundancy = self._redundancy(
            metadatas,
        )

        diversity = self._diversity(
            redundancy,
        )

        spread = self._semantic_spread(
            retrieval,
        )

        quality = self._overall_quality(
            coverage,
            diversity,
            spread,
        )

        return {

            "coverage": round(
                coverage,
                3,
            ),

            "redundancy": round(
                redundancy,
                3,
            ),

            "diversity": round(
                diversity,
                3,
            ),

            "semantic_spread": round(
                spread,
                3,
            ),

            "overall_quality": quality,
        }


retrieval_quality = RetrievalQuality()