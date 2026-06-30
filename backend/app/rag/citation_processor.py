from app.rag.citation_processor_config import CitationProcessorConfig


class CitationProcessor:
    """
    Post-processes answers for citation support.

    Responsibilities

    • Build source mappings
    • Reserve citation numbering
    • Prepare future inline citations
    • Keep citation logic independent from answer generation

    Future responsibilities

    • Inline citation insertion
    • Citation validation
    • Citation deduplication
    • Multiple citation styles
    """

    def __init__(
        self,
        config: CitationProcessorConfig | None = None
    ):

        self.config = config or CitationProcessorConfig()

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

    def _build_citations(
        self,
        answer: str,
        source_mapping: list[dict]
    ) -> tuple[str, list[str]]:

        if not self.config.include_inline_citations:
            return answer, []

        citations = [
            item["citation"]
            for item in source_mapping
        ]

        return answer, citations

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def process(
        self,
        answer: str,
        sources: list[dict]
    ) -> dict:
        """
        Prepare an answer for future citation support.

        The answer itself is intentionally left
        unchanged in this milestone. This component
        establishes the architecture for future
        inline citation insertion.
        """

        source_mapping = self._build_source_mapping(
            sources
        )

        answer, citations = self._build_citations(
            answer,
            source_mapping
        )

        return {
            "answer": answer,
            "citations": citations,
            "source_mapping": source_mapping,
        }


citation_processor = CitationProcessor()