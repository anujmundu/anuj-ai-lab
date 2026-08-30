import re


class ContextCompressor:
    """
    Cleans retrieved documents before context construction.

    Responsibilities

    • Remove duplicate documents
    • Remove empty documents
    • Normalize whitespace
    • Preserve document/metadata alignment

    Future responsibilities

    • Token budget trimming
    • Semantic compression
    • Chunk merging
    • Context window optimization
    """

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _normalize(
        self,
        text: str,
    ) -> str:
        """
        Normalize whitespace while preserving content.
        """

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def compress(
        self,
        *,
        documents: list[str],
        metadatas: list[dict],
    ) -> tuple[list[str], list[dict]]:
        """
        Compress retrieved documents.

        Returns
        -------
        (
            compressed_documents,
            compressed_metadatas,
        )
        """

        compressed_documents: list[str] = []
        compressed_metadatas: list[dict] = []

        seen: set[str] = set()

        for document, metadata in zip(
            documents,
            metadatas,
        ):

            document = self._normalize(
                document,
            )

            # Skip empty chunks

            if not document:
                continue

            # Skip duplicates

            if document in seen:
                continue

            seen.add(
                document,
            )

            compressed_documents.append(
                document,
            )

            compressed_metadatas.append(
                metadata,
            )

        return (
            compressed_documents,
            compressed_metadatas,
        )


context_compressor = ContextCompressor()