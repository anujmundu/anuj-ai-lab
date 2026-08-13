from __future__ import annotations

from app.rag.evaluation.models import (
    AnswerEvaluationResult,
    EvaluationSample,
)


class AnswerEvaluator:
    """
    Converts existing RAG verification outputs into
    standardized answer-evaluation metrics.

    This component does not perform:
    - hallucination detection
    - evidence alignment
    - citation matching
    - answer generation

    It only evaluates/adapts results already produced by
    the existing RAG verification pipeline.
    """

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _evidence_metrics(
        grounding_result: dict,
    ) -> dict:

        metrics = grounding_result.get(
            "metrics",
            {},
        )

        if not isinstance(metrics, dict):
            return {}

        evidence = metrics.get(
            "evidence",
            {},
        )

        if not isinstance(evidence, dict):
            return {}

        return evidence

    @staticmethod
    def _float_or_default(
        value: object,
        default: float = 0.0,
    ) -> float:

        if value is None:
            return default

        if isinstance(value, bool):
            return default

        if isinstance(value, (int, float)):
            return float(value)

        return default

    @classmethod
    def _grounding_score(
        cls,
        grounding_result: dict,
    ) -> float:

        evidence = cls._evidence_metrics(
            grounding_result
        )

        return cls._float_or_default(
            evidence.get(
                "grounding_score"
            )
        )

    @classmethod
    def _supported_ratio(
        cls,
        grounding_result: dict,
    ) -> float:

        evidence = cls._evidence_metrics(
            grounding_result
        )

        return cls._float_or_default(
            evidence.get(
                "supported_ratio"
            )
        )

    @classmethod
    def _unsupported_ratio(
        cls,
        grounding_result: dict,
    ) -> float:

        evidence = cls._evidence_metrics(
            grounding_result
        )

        return cls._float_or_default(
            evidence.get(
                "unsupported_ratio"
            )
        )

    @classmethod
    def _average_confidence(
        cls,
        grounding_result: dict,
    ) -> float:

        evidence = cls._evidence_metrics(
            grounding_result
        )

        return cls._float_or_default(
            evidence.get(
                "average_confidence"
            )
        )

    @classmethod
    def _hallucination_risk(
        cls,
        hallucination: dict,
    ) -> float | None:

        value = hallucination.get(
            "hallucination_risk"
        )

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        return None

    @classmethod
    def _citation_coverage(
        cls,
        citations: dict,
    ) -> float:

        coverage = citations.get(
            "coverage",
            {},
        )

        if not isinstance(coverage, dict):
            return 0.0

        return cls._float_or_default(
            coverage.get(
                "coverage"
            )
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def evaluate(
        self,
        *,
        sample: EvaluationSample,
        grounding_result: dict,
        hallucination: dict,
        citations: dict,
    ) -> AnswerEvaluationResult:
        """
        Evaluate one generated answer using existing
        verification outputs.
        """

        grounding_score = (
            self._grounding_score(
                grounding_result
            )
        )

        supported_ratio = (
            self._supported_ratio(
                grounding_result
            )
        )

        unsupported_ratio = (
            self._unsupported_ratio(
                grounding_result
            )
        )

        average_confidence = (
            self._average_confidence(
                grounding_result
            )
        )

        hallucination_risk = (
            self._hallucination_risk(
                hallucination
            )
        )

        citation_coverage = (
            self._citation_coverage(
                citations
            )
        )

        grounding_decision = (
            grounding_result.get(
                "decision",
                "",
            )
        )

        grounded = bool(
            grounding_result.get(
                "grounded",
                False,
            )
        )

        repairable = bool(
            grounding_result.get(
                "repairable",
                False,
            )
        )

        return AnswerEvaluationResult(
            sample_id=sample.sample_id,

            grounding_score=round(
                grounding_score,
                4,
            ),

            supported_ratio=round(
                supported_ratio,
                4,
            ),

            unsupported_ratio=round(
                unsupported_ratio,
                4,
            ),

            average_confidence=round(
                average_confidence,
                4,
            ),

            hallucination_risk=(
                round(
                    hallucination_risk,
                    4,
                )
                if hallucination_risk is not None
                else None
            ),

            # No independent consistency algorithm is
            # introduced in this phase. This remains
            # unavailable until the existing pipeline
            # exposes a consistency metric.
            consistency_score=0.0,

            citation_coverage=round(
                citation_coverage,
                4,
            ),

            grounding_decision=(
                grounding_decision
                if isinstance(
                    grounding_decision,
                    str,
                )
                else ""
            ),

            grounded=grounded,

            repairable=repairable,
        )


answer_evaluator = AnswerEvaluator()