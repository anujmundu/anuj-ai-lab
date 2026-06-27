from collections import OrderedDict

from app.rag.context_builder_config import ContextBuilderConfig


class ContextBuilder:
    """
    Builds structured context for the LLM.

    Responsibilities

    • Group retrieved chunks by document
    • Preserve retrieval order by default
    • Produce readable context

    Future responsibilities

    • Context compression
    • Token budgeting
    • Citation formatting
    • Context deduplication
    """

    def __init__(
        self,
        config: ContextBuilderConfig | None = None
    ):

        self.config = config or ContextBuilderConfig()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _separator(self) -> str:

        if self.config.separator_style == "double_line":
            return "=" * 50

        return "-" * 50

    def _group_by_document(
        self,
        documents: list[str],
        metadatas: list[dict]
    ) -> OrderedDict[str, list[tuple[dict, str]]]:
        """
        Groups retrieved chunks by filename.

        Retrieval order is preserved by default.
        Optionally reconstructs original document
        order when configured.
        """

        grouped: OrderedDict[
            str,
            list[tuple[dict, str]]
        ] = OrderedDict()

        for metadata, document in zip(
            metadatas,
            documents
        ):

            filename = metadata["filename"]

            grouped.setdefault(
                filename,
                []
            ).append(
                (
                    metadata,
                    document
                )
            )

        #
        # Optional ordering.
        #
        # Retrieval order (default)
        # preserves ranking.
        #
        # Document order reconstructs
        # the original document.
        #

        if self.config.chunk_order == "document":

            for chunks in grouped.values():

                chunks.sort(
                    key=lambda item: item[0]["chunk_number"]
                )

        return grouped

    def _build_document_header(
        self,
        filename: str
    ) -> list[str]:

        if not self.config.include_document_headers:
            return []

        separator = self._separator()

        return [
            separator,
            f"Document: {filename}.txt",
            separator,
            ""
        ]

    def _build_chunk_header(
        self,
        metadata: dict
    ) -> list[str]:

        if not self.config.include_chunk_headers:
            return []

        lines: list[str] = []

        if self.config.include_chunk_numbers:

            lines.append(
                f"Chunk {metadata['chunk_number']} / "
                f"{metadata['total_chunks']}"
            )

        else:

            lines.append("Chunk")

        lines.append("")

        return lines

    def _iter_document_sections(
        self,
        grouped: OrderedDict[
            str,
            list[tuple[dict, str]]
        ]
    ):
        """
        Yields each document section.

        Separating iteration from formatting keeps
        build_context() small and allows diagnostic
        tools to reuse the exact production grouping.
        """

        for filename, chunks in grouped.items():

            yield filename, chunks

    def _build_document_section(
        self,
        filename: str,
        chunks: list[tuple[dict, str]]
    ) -> list[str]:

        lines: list[str] = []

        lines.extend(
            self._build_document_header(
                filename
            )
        )

        for metadata, document in chunks:

            lines.extend(
                self._build_chunk_header(
                    metadata
                )
            )

            lines.append(
                document.strip()
            )

            lines.append("")
            lines.append("-" * 50)
            lines.append("")

        return lines

    def _truncate_context(
        self,
        context: str
    ) -> str:

        limit = self.config.max_context_characters

        if limit is None:
            return context

        if len(context) <= limit:
            return context

        return context[:limit].rstrip()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def build_context(
        self,
        documents: list[str],
        metadatas: list[dict]
    ) -> str:

        if not documents:
            return ""

        if not self.config.group_by_document:

            context = "\n\n".join(
                document.strip()
                for document in documents
            )

            return self._truncate_context(
                context
            )

        grouped = self._group_by_document(
            documents,
            metadatas
        )

        lines: list[str] = []

        for filename, chunks in self._iter_document_sections(
            grouped
        ):

            lines.extend(
                self._build_document_section(
                    filename,
                    chunks
                )
            )

        context = "\n".join(lines).strip()

        return self._truncate_context(
            context
        )


context_builder = ContextBuilder()