import re

from app.rag.citation_processor_config import CitationProcessorConfig


class CitationProcessor:
    """
    Post-processes answers for citation support.

    Responsibilities

    • Build source mappings
    • Extract inline citations
    • Validate citation references
    • Keep citation logic independent from answer generation

    Future responsibilities

    • Citation validation against sources
    • Citation deduplication
    • Multiple citation styles
    """

    def __init__(
        self,
        config: CitationProcessorConfig | None = None
    ):

        self.config = (
            config
            or CitationProcessorConfig()
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _build_source_mapping(
        self,
        sources: list[dict]
    ) -> list[dict]:

        if not self.config.include_source_mapping:
            return []

        mapping: list[dict] = []

        for index, source in enumerate(
            sources,
            start=1
        ):

            mapping.append(
                {
                    "citation": (
                        f"{self.config.citation_prefix}"
                        f"{index}"
                        f"{self.config.citation_suffix}"
                    ),
                    "filename": source["filename"],
                    "chunk_id": source["chunk_id"],
                    "chunk_number": source["chunk_number"],
                    "total_chunks": source["total_chunks"],
                }
            )

        return mapping

    def _extract_citations(
        self,
        answer: str
    ) -> list[str]:
        """
        Extract inline citations that already
        exist in the generated answer.

        Example:
            "...Python... [1] [2]"

        Returns:
            ["[1]", "[2]"]
        """

        citations = re.findall(
            r"\[\d+\]",
            answer,
        )

        # Preserve order while removing duplicates.
        return list(
            dict.fromkeys(citations)
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def process(
        self,
        answer: str,
        sources: list[dict]
    ) -> dict:
        """
        Build citation diagnostics.

        Inline citation insertion is handled by
        citation_inserter.py.

        This component extracts citations from the
        final answer and maps them back to the
        retrieved source chunks.
        """

        source_mapping = (
            self._build_source_mapping(
                sources
            )
        )

        citations = self._extract_citations(
            answer
        )

        return {
            "answer": answer,
            "citations": citations,
            "source_mapping": source_mapping,
        }


citation_processor = CitationProcessor()