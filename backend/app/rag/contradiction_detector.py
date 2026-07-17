from app.rag.contradiction_detector_config import (
    ContradictionDetectorConfig,
)

from app.rag.embedding_similarity import (
    embedding_similarity,
)


class ContradictionDetector:
    """
    Determines whether a claim is supported
    by retrieved context.

    Current implementation is heuristic.

    IMPORTANT

    Low semantic similarity does NOT imply
    contradiction.

    Therefore:

        high similarity   -> supported
        medium similarity -> neutral
        low similarity    -> neutral

    Only extremely low similarity is treated
    as a possible contradiction until a true
    NLI model replaces this module.
    """

    def __init__(
        self,
        config: ContradictionDetectorConfig | None = None,
    ):

        self.config = (
            config
            or ContradictionDetectorConfig()
        )
        
        # --------------------------------------------------

    NEGATIONS = {
        "not",
        "no",
        "never",
        "without",
        "none",
        "cannot",
        "can't",
        "doesn't",
        "don't",
        "isn't",
        "wasn't",
        "weren't",
        "won't",
        "shouldn't",
        "couldn't",
    }

    def _contains_negation_conflict(
        self,
        claim: str,
        context: str,
    ) -> bool:

        claim_words = {
            word.lower()
            for word in claim.split()
        }

        context_words = {
            word.lower()
            for word in context.split()
        }

        claim_negation = bool(
            claim_words & self.NEGATIONS
        )

        context_negation = bool(
            context_words & self.NEGATIONS
        )

        return claim_negation != context_negation

    # --------------------------------------------------

    def evaluate(
        self,
        *,
        claim: str,
        context: str,
        similarity: dict | None = None,
    ) -> dict:

        if not self.config.enabled:

            return {}

        if similarity is None:

            similarity = (
                embedding_similarity.compare(
                    claim,
                    context,
                )
            )

        score = similarity["similarity"]

        # --------------------------------------------------
        # Supported
        # --------------------------------------------------

        if score >= self.config.support_threshold:

            label = "supported"

            support = score

            neutral = 1.0 - score

            contradiction = 0.0

        elif score >= self.config.neutral_threshold:

            label = "neutral"

            support = score * 0.50

            neutral = score

            contradiction = (1.0 - score) * 0.50

        else:

            label = "unrelated"

            support = 0.0

            neutral = 1.0

            contradiction = 0.0

        # ----------------------------------------------
        # Explicit contradiction detection
        # ----------------------------------------------

        if self._contains_negation_conflict(
            claim,
            context,
        ):

            label = "contradicted"

            support = 0.0

            neutral = 0.0

            contradiction = 1.0

        result = {

            "label": label,

            "support": round(
                support,
                3,
            ),

            "neutral": round(
                neutral,
                3,
            ),

            "contradiction": round(
                contradiction,
                3,
            ),

            "score": round(
                score,
                3,
            ),
        }

        if self.config.include_similarity:

            result["similarity"] = similarity

        if self.config.include_explanation:

            result["explanation"] = {

                "reason": similarity[
                    "explanation"
                ]
            }

        if self.config.include_diagnostics:

            result["diagnostics"] = {

                "confidence": similarity[
                    "confidence"
                ]
            }

        return result


contradiction_detector = (
    ContradictionDetector()
)