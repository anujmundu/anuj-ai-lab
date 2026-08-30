from dataclasses import dataclass, field


@dataclass(slots=True)
class CitationGrounderConfig:
    """
    Configuration for semantic citation grounding.

    This module determines how confidently
    answer sentences are linked to retrieved
    source chunks.

    It does NOT perform retrieval.
    It only evaluates grounding quality.
    """

    # --------------------------------------------------
    # Master Switches
    # --------------------------------------------------

    enabled: bool = True

    enable_semantic_matching: bool = True

    enable_multi_citation: bool = True

    enable_confidence_scoring: bool = True

    include_similarity_breakdown: bool = True

    # --------------------------------------------------
    # Sentence Processing
    # --------------------------------------------------

    sentence_split_pattern: str = (
        r"(?<=[.!?])\s+"
    )

    ignore_non_text_sentences: bool = True

    minimum_sentence_length: int = 15

    # --------------------------------------------------
    # Semantic Matching
    # --------------------------------------------------

    minimum_similarity: float = 0.35

    partial_grounding_threshold: float = 0.45

    grounded_threshold: float = 0.70

    maximum_sources_per_sentence: int = 3

    # --------------------------------------------------
    # Confidence Thresholds
    # --------------------------------------------------

    high_confidence: float = 0.85

    medium_confidence: float = 0.65

    low_confidence: float = 0.45

    # --------------------------------------------------
    # Diagnostic Output
    # --------------------------------------------------

    include_sentence_scores: bool = True

    include_source_matches: bool = True

    include_grounding_summary: bool = True

    include_confidence_summary: bool = True
