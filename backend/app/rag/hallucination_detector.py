import re

from app.rag.hallucination_detector_config import (
    HallucinationDetectorConfig,
)

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "by",
    "for",
    "from",
    "have",
    "has",
    "had",
    "i",
    "in",
    "including",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "there",
    "they",
    "this",
    "to",
    "was",
    "were",
    "with",
    "you",
    "your",
}

FALLBACK_RESPONSES = (
    "i don't have enough information",
    "i do not have enough information",
    "i don't know",
    "i do not know",
    "not enough information",
)

class HallucinationDetector:
    """
    Estimates hallucination risk for generated answers.

    Responsibilities

    • Normalize text
    • Compare answer against retrieved context
    • Identify unsupported terms
    • Estimate hallucination risk

    Future responsibilities

    • Sentence-level verification
    • Source attribution checks
    • LLM self-verification
    • Cross-document consistency
    """

    def __init__(
        self,
        config: HallucinationDetectorConfig | None = None
    ):

        self.config = (
            config
            or HallucinationDetectorConfig()
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _normalize_text(
        self,
        text: str
    ) -> str:

        if not self.config.normalize_text:
            return text

        if self.config.ignore_case:
            text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()

    def _tokenize(
        self,
        text: str
    ) -> set[str]:

        text = self._normalize_text(text)

        tokens = set(
            re.findall(
                r"\b\w+\b",
                text
            )
        )

        tokens = {
            token
            for token in tokens
            if (
                len(token)
                >= self.config.minimum_token_length
                and token not in STOPWORDS
            )
        }

        return tokens
    
    def _is_fallback_response(
        self,
        answer: str,
    ) -> bool:
        """
        Detect known fallback responses that intentionally
        avoid making unsupported claims.
        """

        normalized = self._normalize_text(answer)

        return any(
            normalized.startswith(response)
            for response in FALLBACK_RESPONSES
        )

    def _context_overlap(
        self,
        answer_tokens: set[str],
        context_tokens: set[str]
    ) -> float:

        if (
            not self.config.check_context_overlap
            or not answer_tokens
        ):
            return 0.0

        supported = (
            answer_tokens
            & context_tokens
        )
        
        coverage = (
            len(supported) / len(answer_tokens)
            if answer_tokens
            else 0.0
        )

        return len(supported) / len(answer_tokens)

    def _unsupported_terms(
        self,
        answer_tokens: set[str],
        context_tokens: set[str]
    ) -> list[str]:

        if not self.config.detect_unsupported_terms:
            return []

        unsupported = (
            answer_tokens
            - context_tokens
        )

        return sorted(
            unsupported
        )

    def _estimate_hallucination_risk(
        self,
        overlap: float
    ) -> float:

        if not self.config.estimate_hallucination_risk:
            return 0.0

        risk = 1.0 - overlap

        return round(
            max(
                0.0,
                min(
                    risk,
                    1.0
                )
            ),
            2
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def detect(
        self,
        answer: str,
        context: str
    ) -> dict:
        """
        Analyze an answer against the retrieved
        context.

        Returns diagnostics only.
        Does not modify the answer.
        """

        answer_tokens = self._tokenize(
            answer
        )

        context_tokens = self._tokenize(
            context
        )
        
        is_fallback = self._is_fallback_response(
            answer
        )

        if is_fallback:
            return {
                "hallucination_analysis": "not_applicable",
                "reason": "fallback_response",
                "hallucination_risk": None,
                "context_overlap": None,
                "supported_terms": None,
                "unsupported_terms": None,
                "unsupported_term_list": [],
                "is_potential_hallucination": False,
            }

        overlap = self._context_overlap(
            answer_tokens,
            context_tokens
        )

        unsupported = self._unsupported_terms(
            answer_tokens,
            context_tokens
        )

        risk = (
            self._estimate_hallucination_risk(
                overlap
            )
        )

        supported = (
            len(answer_tokens)
            - len(unsupported)
        )
        
        coverage = (
            supported / len(answer_tokens)
            if answer_tokens
            else 0.0
        )

        return {
            "hallucination_risk": risk,

            "coverage": round(
                coverage,
                2,
            ),

            "context_overlap": round(
                overlap,
                2,
            ),

            "normalized_overlap": round(
                overlap,
                2,
            ),

            "supported_terms": supported,

            "unsupported_terms": len(
                unsupported
            ),

            "analyzed_answer_tokens": len(
                answer_tokens
            ),

            "analyzed_context_tokens": len(
                context_tokens
            ),

            "unsupported_term_list": unsupported,

            "is_potential_hallucination": (
                risk >= self.config.risk_threshold
            ),
        }


hallucination_detector = (
    HallucinationDetector()
)