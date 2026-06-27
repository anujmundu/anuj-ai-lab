from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class ContextBuilderConfig:
    """
    Configuration for ContextBuilder.

    Controls how retrieved chunks are assembled
    before being sent to the LLM.
    """

    # --------------------------------------------------
    # Document Grouping
    # --------------------------------------------------

    group_by_document: bool = True

    # Preserve retrieval ranking or reconstruct
    # the original document order.
    chunk_order: Literal[
        "retrieval",
        "document"
    ] = "retrieval"

    # --------------------------------------------------
    # Formatting
    # --------------------------------------------------

    include_document_headers: bool = True

    include_chunk_headers: bool = True

    include_chunk_numbers: bool = True

    separator_style: Literal[
        "single_line",
        "double_line"
    ] = "double_line"

    # --------------------------------------------------
    # Future Context Compression
    # --------------------------------------------------

    max_context_characters: int | None = None