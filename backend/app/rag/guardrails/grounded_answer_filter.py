from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.rag.evidence_models import EvidenceAlignmentResult


class GroundingDecision(str, Enum):
    """
    Final deterministic decision for a generated answer.

    ACCEPT:
        The answer has sufficient evidence support.

    REPAIR:
        The answer contains weak or partially supported
        content but enough evidence exists for a future
        constrained repair step.

    REJECT:
        The answer is insufficiently grounded or contains
        significant contradiction / hallucination risk.
    """

    ACCEPT = "accept"
    REPAIR = "repair"
    REJECT = "reject"


@dataclass(slots=True)
class GroundedAnswerFilterConfig:
    """
    Configuration for the grounded-answer decision layer.

    This component does not calculate semantic similarity,
    hallucination risk, or consistency itself.

    Those responsibilities remain delegated to:

        EvidenceAligner
        HallucinationDetector
        AnswerConsistencyChecker

    This class only combines their outputs into a final
    deterministic decision.
    """

    enabled: bool = True

    # --------------------------------------------------
    # Evidence thresholds
    # --------------------------------------------------

    minimum_grounding_score: float = 0.70

    minimum_average_confidence: float = 0.60

    # Minimum percentage of answer sentences that should
    # have at least partial evidence support.
    minimum_supported_ratio: float = 0.70

    # --------------------------------------------------
    # Hallucination thresholds
    # --------------------------------------------------

    maximum_hallucination_risk: float = 0.50

    maximum_unsupported_sentence_ratio: float = 0.30

    # --------------------------------------------------
    # Consistency thresholds
    # --------------------------------------------------

    minimum_consistency_score: float = 0.70

    maximum_contradicted_pairs: int = 0

    # --------------------------------------------------
    # Decision policy
    # --------------------------------------------------

    # If the answer is not completely grounded but still
    # contains enough evidence for a future repair step,
    # return REPAIR instead of immediately rejecting it.
    enable_repair_state: bool = True


# Singleton configuration.
grounded_answer_filter_config = GroundedAnswerFilterConfig()


class GroundedAnswerFilter:
    """
    Deterministic grounding decision layer.

    The filter does NOT:

        - retrieve documents
        - generate answers
        - calculate embeddings
        - perform semantic matching
        - detect hallucinations independently
        - perform NLI independently
        - insert citations
        - rewrite answers

    It consumes the outputs of existing verification
    components and determines whether the generated answer
    should be accepted, repaired, or rejected.

    Architecture:

        LLM Answer
             |
             +----------------------+
             |                      |
             v                      v
       EvidenceAligner       HallucinationDetector
             |                      |
             +----------+-----------+
                        |
                        v
               AnswerConsistencyChecker
                        |
                        v
              GroundedAnswerFilter
                        |
              +---------+---------+
              |         |         |
              v         v         v
           ACCEPT     REPAIR    REJECT
    """

    def __init__(
        self,
        config: GroundedAnswerFilterConfig | None = None,
    ) -> None:

        self.config = (
            config
            or grounded_answer_filter_config
        )

    # ==================================================
    # Generic Helpers
    # ==================================================

    @staticmethod
    def _clamp(
        value: float,
    ) -> float:
        """
        Clamp a numeric value to [0, 1].
        """

        return max(
            0.0,
            min(
                float(value),
                1.0,
            ),
        )

    @staticmethod
    def _safe_float(
        value: Any,
        default: float = 0.0,
    ) -> float:
        """
        Safely convert a value to float.
        """

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return default

    @staticmethod
    def _safe_int(
        value: Any,
        default: int = 0,
    ) -> int:
        """
        Safely convert a value to int.
        """

        try:
            return int(value)
        except (
            TypeError,
            ValueError,
        ):
            return default

    # ==================================================
    # Evidence Analysis
    # ==================================================

    def _extract_evidence_metrics(
        self,
        alignment: EvidenceAlignmentResult,
    ) -> dict:
        """
        Extract evidence-grounding metrics from
        EvidenceAlignmentResult.

        EvidenceAligner is the authoritative source for
        sentence-level evidence support.
        """

        total_sentences = len(
            alignment.sentences
        )

        grounded_sentences = self._safe_int(
            alignment.grounded_count
        )

        partial_sentences = self._safe_int(
            alignment.partial_count
        )

        unsupported_sentences = self._safe_int(
            alignment.unsupported_count
        )

        grounding_score = self._safe_float(
            getattr(
                alignment,
                "grounding_score",
                0.0,
            )
        )

        average_confidence = self._safe_float(
            alignment.average_confidence
        )

        if total_sentences:

            supported_sentences = (
                grounded_sentences
                + partial_sentences
            )

            supported_ratio = (
                supported_sentences
                / total_sentences
            )

            unsupported_ratio = (
                unsupported_sentences
                / total_sentences
            )

        else:

            supported_ratio = 0.0
            unsupported_ratio = 0.0

        return {
            "total_sentences": total_sentences,
            "grounded_sentences": grounded_sentences,
            "partially_grounded_sentences": (
                partial_sentences
            ),
            "unsupported_sentences": (
                unsupported_sentences
            ),
            "supported_ratio": round(
                supported_ratio,
                3,
            ),
            "unsupported_ratio": round(
                unsupported_ratio,
                3,
            ),
            "grounding_score": round(
                self._clamp(
                    grounding_score
                ),
                3,
            ),
            "average_confidence": round(
                self._clamp(
                    average_confidence
                ),
                3,
            ),
        }

    # ==================================================
    # Hallucination Analysis
    # ==================================================

    def _extract_hallucination_metrics(
        self,
        hallucination: dict | None,
    ) -> dict:
        """
        Extract hallucination-related metrics from the
        existing HallucinationDetector result.

        The filter does not independently perform
        hallucination detection.
        """

        hallucination = (
            hallucination
            or {}
        )

        risk = self._safe_float(
            hallucination.get(
                "hallucination_risk",
                hallucination.get(
                    "risk",
                    0.0,
                ),
            )
        )

        unsupported_claims = self._safe_int(
            hallucination.get(
                "unsupported_claims",
                hallucination.get(
                    "unsupported_sentences",
                    0,
                ),
            )
        )

        contradicted_claims = self._safe_int(
            hallucination.get(
                "contradicted_claims",
                0,
            )
        )

        contradictions_detected = self._safe_int(
            hallucination.get(
                "contradictions_detected",
                0,
            )
        )

        return {
            "hallucination_risk": round(
                self._clamp(risk),
                3,
            ),
            "unsupported_claims": (
                unsupported_claims
            ),
            "contradicted_claims": (
                contradicted_claims
            ),
            "contradictions_detected": (
                contradictions_detected
            ),
        }

    # ==================================================
    # Consistency Analysis
    # ==================================================

    def _extract_consistency_metrics(
        self,
        consistency: dict | None,
    ) -> dict:
        """
        Extract consistency metrics from the existing
        AnswerConsistencyChecker.

        The consistency checker remains responsible for
        sentence-pair comparison and contradiction
        detection.
        """

        consistency = (
            consistency
            or {}
        )

        consistency_score = self._safe_float(
            consistency.get(
                "consistency_score",
                1.0,
            ),
            default=1.0,
        )

        contradicted_pairs = self._safe_int(
            consistency.get(
                "contradicted_pairs",
                0,
            )
        )

        status = consistency.get(
            "status",
            "unknown",
        )

        return {
            "status": status,
            "consistency_score": round(
                self._clamp(
                    consistency_score
                ),
                3,
            ),
            "contradicted_pairs": (
                contradicted_pairs
            ),
            "sentence_pairs": self._safe_int(
                consistency.get(
                    "sentence_pairs",
                    0,
                )
            ),
        }

    # ==================================================
    # Hard Failure Detection
    # ==================================================

    def _has_hard_failure(
        self,
        evidence: dict,
        hallucination: dict,
        consistency: dict,
    ) -> tuple[bool, list[str]]:
        """
        Determine whether the answer contains conditions
        severe enough to prevent acceptance.

        Returns:

            (failed, reasons)
        """

        reasons: list[str] = []

        # ----------------------------------------------
        # Unsupported evidence
        # ----------------------------------------------

        if (
            evidence["unsupported_ratio"]
            > self.config.maximum_unsupported_sentence_ratio
        ):

            reasons.append(
                "unsupported_sentence_ratio_exceeded"
            )

        # ----------------------------------------------
        # Hallucination risk
        # ----------------------------------------------

        if (
            hallucination["hallucination_risk"]
            > self.config.maximum_hallucination_risk
        ):

            reasons.append(
                "hallucination_risk_exceeded"
            )

        # ----------------------------------------------
        # Contradicted claims
        # ----------------------------------------------

        if (
            hallucination["contradicted_claims"]
            > 0
        ):

            reasons.append(
                "contradicted_claims_detected"
            )

        # ----------------------------------------------
        # Explicit contradiction detection
        # ----------------------------------------------

        if (
            hallucination["contradictions_detected"]
            > 0
        ):

            reasons.append(
                "hallucination_detector_found_contradictions"
            )

        if (
            consistency["contradicted_pairs"]
            > self.config.maximum_contradicted_pairs
        ):

            reasons.append(
                "contradicted_sentence_pairs_detected"
            )

        return (
            bool(reasons),
            reasons,
        )

    # ==================================================
    # Acceptance
    # ==================================================

    def _meets_acceptance_criteria(
        self,
        evidence: dict,
        hallucination: dict,
        consistency: dict,
    ) -> tuple[bool, list[str]]:
        """
        Determine whether the answer is sufficiently
        grounded to be accepted.
        """

        reasons: list[str] = []

        if (
            evidence["grounding_score"]
            < self.config.minimum_grounding_score
        ):

            reasons.append(
                "grounding_score_below_threshold"
            )

        if (
            evidence["average_confidence"]
            < self.config.minimum_average_confidence
        ):

            reasons.append(
                "average_evidence_confidence_below_threshold"
            )

        if (
            evidence["supported_ratio"]
            < self.config.minimum_supported_ratio
        ):

            reasons.append(
                "supported_sentence_ratio_below_threshold"
            )

        if (
            hallucination["hallucination_risk"]
            > self.config.maximum_hallucination_risk
        ):

            reasons.append(
                "hallucination_risk_above_threshold"
            )

        if (
            consistency["consistency_score"]
            < self.config.minimum_consistency_score
        ):

            reasons.append(
                "consistency_score_below_threshold"
            )

        if (
            consistency["contradicted_pairs"]
            > self.config.maximum_contradicted_pairs
        ):

            reasons.append(
                "contradicted_sentence_pairs_present"
            )

        return (
            not reasons,
            reasons,
        )

    # ==================================================
    # Repair Eligibility
    # ==================================================

    def _is_repairable(
        self,
        evidence: dict,
        hallucination: dict,
        consistency: dict,
    ) -> tuple[bool, list[str]]:
        """
        Determine whether the answer is weak but still
        suitable for a future constrained repair operation.

        Important:

        This method does NOT repair the answer.

        It only identifies a state in which a future
        repair component could safely operate.
        """

        reasons: list[str] = []

        # ----------------------------------------------
        # Completely unsupported answers are not
        # considered repairable.
        # ----------------------------------------------

        if (
            evidence["supported_ratio"]
            <= 0.0
        ):

            reasons.append(
                "no_supported_sentences"
            )

            return (
                False,
                reasons,
            )

        # ----------------------------------------------
        # Severe hallucination risk should be rejected.
        # ----------------------------------------------

        if (
            hallucination["hallucination_risk"]
            > self.config.maximum_hallucination_risk
        ):

            reasons.append(
                "hallucination_risk_too_high"
            )

            return (
                False,
                reasons,
            )

        # ----------------------------------------------
        # Explicit contradictions are not repairable by
        # a simple grounding repair.
        # ----------------------------------------------

        if (
            hallucination["contradicted_claims"]
            > 0
            or hallucination["contradictions_detected"]
            > 0
            or consistency["contradicted_pairs"]
            > 0
        ):

            reasons.append(
                "contradictions_require_rejection"
            )

            return (
                False,
                reasons,
            )

        # ----------------------------------------------
        # Some evidence exists, but acceptance criteria
        # were not fully satisfied.
        # ----------------------------------------------

        if (
            evidence["grounded_sentences"] > 0
            or evidence["partially_grounded_sentences"] > 0
        ):

            reasons.append(
                "partial_evidence_available"
            )

            return (
                True,
                reasons,
            )

        return (
            False,
            reasons,
        )

    # ==================================================
    # Main Evaluation
    # ==================================================

    def evaluate(
        self,
        *,
        answer: str,
        alignment: EvidenceAlignmentResult,
        hallucination: dict | None = None,
        consistency: dict | None = None,
        citation_result: dict | None = None,
    ) -> dict:
        """
        Evaluate the generated answer.

        Parameters
        ----------
        answer:
            Final/generated answer being evaluated.

        alignment:
            EvidenceAlignmentResult produced by EvidenceAligner.

        hallucination:
            Result produced by HallucinationDetector.

        consistency:
            Result produced by AnswerConsistencyChecker.

        citation_result:
            Result produced by CitationProcessor.

        Returns
        -------
        dict
            Structured grounding decision and diagnostics.
        """

        if not self.config.enabled:

            return {
                "enabled": False,
                "decision": GroundingDecision.ACCEPT.value,
                "grounded": True,
                "repairable": False,
                "reason": "grounding_filter_disabled",
                "reasons": [],
                "metrics": {},
            }

        answer = (
            answer
            if isinstance(answer, str)
            else str(answer or "")
        )

        # --------------------------------------------------
        # Empty answer
        # --------------------------------------------------

        if not answer.strip():

            return {
                "enabled": True,
                "decision": GroundingDecision.REJECT.value,
                "grounded": False,
                "repairable": False,
                "reason": "empty_answer",
                "reasons": [
                    "empty_answer",
                ],
                "metrics": {},
            }

        # --------------------------------------------------
        # Extract metrics
        # --------------------------------------------------

        evidence_metrics = (
            self._extract_evidence_metrics(
                alignment
            )
        )

        hallucination_metrics = (
            self._extract_hallucination_metrics(
                hallucination
            )
        )

        consistency_metrics = (
            self._extract_consistency_metrics(
                consistency
            )
        )

        # --------------------------------------------------
        # Hard failures
        # --------------------------------------------------

        hard_failure, hard_failure_reasons = (
            self._has_hard_failure(
                evidence_metrics,
                hallucination_metrics,
                consistency_metrics,
            )
        )

        # --------------------------------------------------
        # Acceptance
        # --------------------------------------------------

        accepted, acceptance_reasons = (
            self._meets_acceptance_criteria(
                evidence_metrics,
                hallucination_metrics,
                consistency_metrics,
            )
        )

        # --------------------------------------------------
        # Citation diagnostics
        # --------------------------------------------------

        citation_metrics = {}

        if citation_result:

            citation_metrics = {
                "coverage": (
                    citation_result.get(
                        "coverage",
                        {},
                    )
                ),
                "citation_count": len(
                    citation_result.get(
                        "citations",
                        [],
                    )
                ),
            }

        # --------------------------------------------------
        # Hard rejection
        # --------------------------------------------------

        if hard_failure:

            return {
                "enabled": True,
                "decision": GroundingDecision.REJECT.value,
                "grounded": False,
                "repairable": False,
                "reason": hard_failure_reasons[0],
                "reasons": hard_failure_reasons,
                "metrics": {
                    "evidence": evidence_metrics,
                    "hallucination": (
                        hallucination_metrics
                    ),
                    "consistency": (
                        consistency_metrics
                    ),
                    "citations": citation_metrics,
                },
            }

        # --------------------------------------------------
        # Full acceptance
        # --------------------------------------------------

        if accepted:

            return {
                "enabled": True,
                "decision": GroundingDecision.ACCEPT.value,
                "grounded": True,
                "repairable": False,
                "reason": "answer_meets_grounding_criteria",
                "reasons": [],
                "metrics": {
                    "evidence": evidence_metrics,
                    "hallucination": (
                        hallucination_metrics
                    ),
                    "consistency": (
                        consistency_metrics
                    ),
                    "citations": citation_metrics,
                },
            }

        # --------------------------------------------------
        # Repair candidate
        # --------------------------------------------------

        repairable, repair_reasons = (
            self._is_repairable(
                evidence_metrics,
                hallucination_metrics,
                consistency_metrics,
            )
        )

        if (
            self.config.enable_repair_state
            and repairable
        ):

            return {
                "enabled": True,
                "decision": GroundingDecision.REPAIR.value,
                "grounded": False,
                "repairable": True,
                "reason": repair_reasons[0],
                "reasons": (
                    acceptance_reasons
                    + repair_reasons
                ),
                "metrics": {
                    "evidence": evidence_metrics,
                    "hallucination": (
                        hallucination_metrics
                    ),
                    "consistency": (
                        consistency_metrics
                    ),
                    "citations": citation_metrics,
                },
            }

        # --------------------------------------------------
        # Final rejection
        # --------------------------------------------------

        return {
            "enabled": True,
            "decision": GroundingDecision.REJECT.value,
            "grounded": False,
            "repairable": False,
            "reason": (
                acceptance_reasons[0]
                if acceptance_reasons
                else "grounding_criteria_not_met"
            ),
            "reasons": acceptance_reasons,
            "metrics": {
                "evidence": evidence_metrics,
                "hallucination": (
                    hallucination_metrics
                ),
                "consistency": (
                    consistency_metrics
                ),
                "citations": citation_metrics,
            },
        }


# ------------------------------------------------------
# Singleton
# ------------------------------------------------------

grounded_answer_filter = GroundedAnswerFilter()
