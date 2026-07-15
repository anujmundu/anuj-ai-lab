from app.rag.pipeline_health_config import (
    PipelineHealthConfig,
)


class PipelineHealth:
    """
    Produces a health report for the
    complete RAG pipeline.

    This component summarizes diagnostics
    already generated elsewhere.
    """

    def __init__(
        self,
        config: PipelineHealthConfig | None = None,
    ):

        self.config = (
            config
            or PipelineHealthConfig()
        )

    # ------------------------------------------

    def _retrieval_health(
        self,
        retrieval_quality: dict,
    ) -> str:

        score = retrieval_quality.get(
            "coverage",
            0.0,
        )

        if score >= self.config.retrieval_good_threshold:
            return "Healthy"

        if score >= self.config.retrieval_fair_threshold:
            return "Fair"

        return "Warning"

    # ------------------------------------------

    def _hallucination_health(
        self,
        hallucination: dict,
    ) -> str:

        risk = hallucination.get(
            "hallucination_risk",
            1.0,
        )

        if risk <= self.config.hallucination_warning_threshold:
            return "Healthy"

        return "Warning"

    # ------------------------------------------

    def _answer_health(
        self,
        answer_quality: dict,
    ) -> str:

        score = answer_quality.get(
            "compression_ratio",
            0.0,
        )

        if score >= self.config.answer_good_threshold:
            return "Healthy"

        if score >= self.config.answer_fair_threshold:
            return "Fair"

        return "Warning"

    # ------------------------------------------

    def evaluate(
        self,
        *,
        retrieval_quality: dict,
        hallucination: dict,
        answer_quality: dict,
    ) -> dict:

        if not self.config.enabled:

            return {}

        retrieval = self._retrieval_health(
            retrieval_quality,
        )

        hallucination_detector = (
            self._hallucination_health(
                hallucination,
            )
        )

        answer = self._answer_health(
            answer_quality,
        )

        statuses = [
            retrieval,
            hallucination_detector,
            answer,
        ]

        if "Warning" in statuses:
            overall = "Warning"

        elif "Fair" in statuses:
            overall = "Fair"

        else:
            overall = "Healthy"

        return {

            "overall": overall,

            "retriever": retrieval,

            "ranker": "Healthy",

            "context_builder": "Healthy",

            "prompt_builder": "Healthy",

            "generator": "Healthy",

            "hallucination_detector": (
                hallucination_detector
            ),

            "citation_grounding": "Healthy",

            "answer_quality": answer,

            "retrieval_quality": retrieval,
        }


pipeline_health = (
    PipelineHealth()
)