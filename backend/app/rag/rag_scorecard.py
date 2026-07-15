from app.rag.rag_scorecard_config import (
    RAGScorecardConfig,
)


class RAGScorecard:
    """
    Produces a high-level scorecard
    summarizing the health of the
    complete RAG pipeline.
    """

    def __init__(
        self,
        config: RAGScorecardConfig | None = None,
    ):

        self.config = (
            config
            or RAGScorecardConfig()
        )

    # -------------------------------------

    @staticmethod
    def _clamp(
        value: float,
    ) -> int:

        value = max(
            0.0,
            min(
                1.0,
                value,
            ),
        )

        return round(
            value * 100
        )

    # -------------------------------------

    @staticmethod
    def _grade(
        score: int,
    ) -> str:

        if score >= 90:
            return "A"

        if score >= 80:
            return "B"

        if score >= 70:
            return "C"

        if score >= 60:
            return "D"

        return "F"

    # -------------------------------------

    def build(
        self,
        *,
        retrieval_quality: dict,
        prompt_quality: dict,
        answer_quality: dict,
        hallucination: dict,
        citations: dict,
    ) -> dict:

        if not self.config.enabled:

            return {}

        retrieval = self._clamp(
            retrieval_quality.get(
                "coverage",
                0.0,
            )
        )

        generation = self._clamp(
            answer_quality.get(
                "compression_ratio",
                0.0,
            )
        )

        grounding = self._clamp(
            1.0
            - hallucination.get(
                "hallucination_risk",
                1.0,
            )
        )

        citation = self._clamp(
            citations.get(
                "coverage",
                {},
            ).get(
                "coverage",
                0.0,
            )
        )

        prompt = self._clamp(
            1.0
            if prompt_quality.get(
                "balanced",
                False,
            )
            else 0.70
        )

        overall = round(
            (
                retrieval
                + generation
                + grounding
                + citation
                + prompt
            )
            / 5
        )

        return {

            "retrieval": retrieval,

            "generation": generation,

            "grounding": grounding,

            "citations": citation,

            "prompt": prompt,

            "overall": overall,

            "grade": self._grade(
                overall,
            ),
        }


rag_scorecard = (
    RAGScorecard()
)