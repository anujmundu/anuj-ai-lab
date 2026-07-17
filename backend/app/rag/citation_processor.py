import re

from app.rag.citation_processor_config import CitationProcessorConfig
from app.rag.citation_grounder import (citation_grounder,)


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
        
    def _normalize_inline_citations(
        self,
        answer: str,
    ) -> str:
        """
        Normalize inline citations so they remain attached
        to the sentence they support.

        Examples

        Sentence.
        [1]

        →

        Sentence. [1]
        """

        answer = re.sub(
            r"\n+\s*(\[\d+\])",
            r" \1",
            answer,
        )

        answer = re.sub(
            r"\s+",
            " ",
            answer,
        )

        return answer.strip()
        
    def _coverage_metrics(
        self,
        answer: str,
        citations: list[str],
    ) -> dict:

        if not self.config.include_coverage_metrics:
            return {}

        answer = self._normalize_inline_citations(
            answer,
        )
        
        sentences = re.split(
            r"(?<=[.!?])\s+(?!\[\d+\])",
            answer.strip(),
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        sentences = [
            sentence
            for sentence in sentences
            if not re.fullmatch(
                r"(?:\[\d+\]\s*)+",
                sentence.strip(),
            )
        ]
        
        total_sentences = len(sentences)

        cited_sentences = sum(
            1
            for sentence in sentences
            if re.search(
                r"\[\d+\]",
                sentence,
            )
        )

        uncited_sentences = (
            total_sentences
            - cited_sentences
        )

        coverage = (
            cited_sentences
            / total_sentences
            if total_sentences
            else 0.0
        )

        density = (
            len(citations)
            / total_sentences
            if total_sentences
            else 0.0
        )

        return {
            "total_sentences": total_sentences,
            "cited_sentences": cited_sentences,
            "uncited_sentences": uncited_sentences,
            "coverage": round(
                coverage,
                2,
            ),
            "citation_density": round(
                density,
                2,
            ),
        } 
        
    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def process(
        self,
        answer: str,
        documents: list[str],
        sources: list[dict],
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
        
        coverage = self._coverage_metrics(
            answer,
            citations,
        )
        
        grounding = (
            citation_grounder.ground(
                answer=answer,
                documents=documents,
                sources=sources,
            )
        )

        return {

            "answer": answer,

            "citations": citations,

            "coverage": coverage,
            
            "grounding": grounding,

            "source_mapping": source_mapping,
        }


citation_processor = CitationProcessor()