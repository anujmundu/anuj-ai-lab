from dataclasses import dataclass


@dataclass(slots=True)
class CitationProcessorConfig:
    """
    Configuration for CitationProcessor.

    Controls how citations are prepared before
    answers are returned to the API.
    """

    # --------------------------------------------------
    # Citation Formatting
    # --------------------------------------------------

    include_inline_citations: bool = False

    include_source_mapping: bool = True

    # --------------------------------------------------
    # Citation Style
    # --------------------------------------------------

    citation_style: str = "numeric"

    citation_prefix: str = "["

    citation_suffix: str = "]"