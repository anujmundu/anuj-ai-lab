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

    def _estimate_confidence(
        self,
        answer: str,
        context: str
    ) -> float:

        if not self.config.estimate_confidence:
            return 1.0

        if not answer:
            return 0.0

        if self._is_unknown_answer(
            answer
        ):
            return 0.0

        confidence = 1.0

        words = len(
            answer.split()
        )

        if words < 5:

            confidence -= 0.50

        elif words < 15:

            confidence -= 0.20

        if not context.strip():

            confidence -= 0.30

        return max(
            0.0,
            min(
                confidence,
                1.0
            )
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