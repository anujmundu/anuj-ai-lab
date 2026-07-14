import re

from app.rag.answer_quality_config import (
    AnswerQualityConfig,
)


class AnswerQuality:
    """
    Computes descriptive quality metrics for
    generated answers.

    Responsibilities

    • Sentence statistics
    • Lexical diversity
    • Repetition estimation
    • Redundancy estimation
    • Readability estimation
    • Compression ratio
    • Overall quality
    """

    def __init__(
        self,
        config: AnswerQualityConfig | None = None,
    ):

        self.config = (
            config
            or AnswerQualityConfig()
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _sentences(
        self,
        text: str,
    ) -> list[str]:

        return [
            sentence.strip()
            for sentence in re.split(
                r"(?<=[.!?])\s+",
                text.strip(),
            )
            if sentence.strip()
        ]

    def _tokens(
        self,
        text: str,
    ) -> list[str]:

        return re.findall(
            r"\b\w+\b",
            text.lower(),
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def analyze(
        self,
        *,
        answer: str,
        prompt: str,
    ) -> dict:

        if not self.config.enabled:

            return {}

        sentences = self._sentences(
            answer,
        )

        tokens = self._tokens(
            answer,
        )

        unique_tokens = set(
            tokens,
        )

        sentence_count = len(
            sentences,
        )

        token_count = len(
            tokens,
        )

        average_sentence_length = (
            token_count / sentence_count
            if sentence_count
            else 0.0
        )

        lexical_diversity = (
            len(unique_tokens) / token_count
            if token_count
            else 0.0
        )

        repetition_ratio = (
            1.0 - lexical_diversity
            if token_count
            else 0.0
        )

        duplicate_tokens = (
            token_count - len(unique_tokens)
        )

        redundancy = (
            duplicate_tokens / token_count
            if token_count
            else 0.0
        )

        if (
            average_sentence_length
            <= self.config.readability_good
        ):

            readability = "Good"

        elif (
            average_sentence_length
            <= self.config.readability_fair
        ):

            readability = "Fair"

        else:

            readability = "Poor"

        compression_ratio = (
            token_count
            / max(
                1,
                len(
                    self._tokens(
                        prompt,
                    )
                ),
            )
        )

        score = 100

        if (
            repetition_ratio
            > self.config.repetition_threshold
        ):
            score -= 20

        if (
            redundancy
            > self.config.redundancy_threshold
        ):
            score -= 20

        if readability == "Fair":
            score -= 10

        elif readability == "Poor":
            score -= 25

        if score >= 85:

            overall = "Excellent"

        elif score >= 70:

            overall = "Good"

        elif score >= 50:

            overall = "Fair"

        else:

            overall = "Poor"

        return {

            "sentence_count": sentence_count,

            "average_sentence_length": round(
                average_sentence_length,
                2,
            ),

            "lexical_diversity": round(
                lexical_diversity,
                3,
            ),

            "repetition_ratio": round(
                repetition_ratio,
                3,
            ),

            "redundancy": round(
                redundancy,
                3,
            ),

            "readability": readability,

            "compression_ratio": round(
                compression_ratio,
                3,
            ),

            "overall_quality": overall,
        }


answer_quality = AnswerQuality()