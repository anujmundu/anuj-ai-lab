from dataclasses import dataclass


@dataclass(slots=True)
class CitationProcessorConfig:
    """
    Configuration for CitationProcessor.

    Controls citation extraction,
    coverage analysis, and grounding
    validation diagnostics.
    """

    # --------------------------------------------------
    # Citation Formatting
    # --------------------------------------------------

    include_inline_citations: bool = False

    include_source_mapping: bool = True

    include_coverage_metrics: bool = True

    # --------------------------------------------------
    # Grounding Validation
    # --------------------------------------------------

    validate_grounding: bool = True

    grounding_threshold: float = 0.50

    partial_grounding_threshold: float = 0.25

    # --------------------------------------------------
    # Text Processing
    # --------------------------------------------------

    ignore_case: bool = True

    minimum_token_length: int = 3

    # --------------------------------------------------
    # Citation Style
    # --------------------------------------------------

    citation_style: str = "numeric"

    citation_prefix: str = "["

    citation_suffix: str = "]"