from dataclasses import dataclass


@dataclass(slots=True)
class AnswerProcessorConfig:
    """
    Configuration for AnswerProcessor.

    Controls how generated answers are
    normalized and validated before they
    are returned by the RAG pipeline.
    """

    # --------------------------------------------------
    # Answer Cleanup
    # --------------------------------------------------

    normalize_whitespace: bool = True

    strip_answer: bool = True

    # --------------------------------------------------
    # Unknown Answer Detection
    # --------------------------------------------------

    preserve_unknown_answer: bool = True

    unknown_answer: str = (
        "I don't have enough information "
        "in the retrieved documents."
    )

    # --------------------------------------------------
    # Confidence
    # --------------------------------------------------

    estimate_confidence: bool = True

    include_confidence: bool = False