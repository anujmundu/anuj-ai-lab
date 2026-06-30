import re

from app.rag.answer_processor_config import AnswerProcessorConfig


class AnswerProcessor:
    """
    Post-processes answers produced by the LLM.

    Responsibilities

    • Normalize whitespace
    • Preserve unknown-answer responses
    • Estimate answer confidence
    • Prepare answers for future post-processing

    Future responsibilities

    • Citation insertion
    • Hallucination detection
    • Markdown formatting
    • Answer rewriting
    """

    def __init__(
        self,
        config: AnswerProcessorConfig | None = None
    ):

        self.config = config or AnswerProcessorConfig()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _strip_answer(
        self,
        answer: str
    ) -> str:

        if not self.config.strip_answer:
            return answer

        return answer.strip()

    def _normalize_whitespace(
        self,
        answer: str
    ) -> str:

        if not self.config.normalize_whitespace:
            return answer

        answer = re.sub(
            r"\s+",
            " ",
            answer
        )

        return answer.strip()

    def _is_unknown_answer(
        self,
        answer: str
    ) -> bool:

        return (
            answer
            == self.config.unknown_answer
        )

    # --------------------------------------------------
    # Confidence Scoring
    # --------------------------------------------------

    def _score_answer_length(
        self,
        answer: str
    ) -> float:

        words = len(answer.split())

        if words == 0:
            return 0.0

        if words < 5:
            return 0.30

        if words < 15:
            return 0.70

        return 1.0

    def _score_context_overlap(
        self,
        answer: str,
        context: str
    ) -> float:

        answer_words = {
            word.lower()
            for word in re.findall(
                r"\w+",
                answer
            )
        }

        context_words = {
            word.lower()
            for word in re.findall(
                r"\w+",
                context
            )
        }

        if not answer_words:
            return 0.0

        overlap = len(
            answer_words & context_words
        )

        return overlap / len(answer_words)

    def _score_answer_completeness(
        self,
        answer: str
    ) -> float:

        answer = answer.strip()

        if not answer:
            return 0.0

        words = answer.split()

        score = 0.0

        if len(words) >= 3:
            score += 0.40

        if len(words) >= 10:
            score += 0.30

        if answer.endswith((".", "!", "?")):
            score += 0.30

        return min(score, 1.0)

    def _estimate_confidence(
        self,
        answer: str,
        context: str
    ) -> float:

        if not self.config.estimate_confidence:
            return 1.0

        if not answer:
            return 0.0

        if self._is_unknown_answer(answer):
            return 0.0

        length_score = self._score_answer_length(
            answer
        )

        overlap_score = self._score_context_overlap(
            answer,
            context
        )

        completeness_score = (
            self._score_answer_completeness(
                answer
            )
        )

        confidence = (
            (0.25 * length_score)
            + (0.40 * overlap_score)
            + (0.35 * completeness_score)
        )

        return round(
            max(
                0.0,
                min(confidence, 1.0)
            ),
            2
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def process(
        self,
        answer: str,
        context: str
    ) -> dict:
        """
        Process the raw LLM answer.

        Orchestrates the answer post-processing
        pipeline while delegating individual tasks
        to specialized helper methods.
        """

        answer = self._strip_answer(
            answer
        )

        answer = self._normalize_whitespace(
            answer
        )

        is_unknown = (
            self._is_unknown_answer(
                answer
            )
            if self.config.preserve_unknown_answer
            else False
        )

        confidence = self._estimate_confidence(
            answer,
            context
        )

        return {
            "answer": answer,
            "confidence": confidence,
            "is_unknown": is_unknown
        }


answer_processor = AnswerProcessor()