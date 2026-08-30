from collections import OrderedDict

from app.rag.context_builder_config import ContextBuilderConfig


class ContextBuilder:
    """
    Builds structured context for the LLM.

    Responsibilities

    • Group retrieved chunks by document
    • Preserve retrieval ranking
    • Produce readable context
    • Respect context budget

    Future responsibilities

    • Context compression
    • Token budgeting
    • Citation formatting
    • Context deduplication
    """

    def __init__(
        self,
        config: ContextBuilderConfig | None = None,
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
        metadatas: list[dict],
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
            documents,
        ):

            filename = metadata["filename"]

            grouped.setdefault(
                filename,
                [],
            ).append(
                (
                    metadata,
                    document,
                )
            )

        #
        # Preserve original document order if requested.
        #

        if self.config.chunk_order == "document":

            for chunks in grouped.values():

                chunks.sort(
                    key=lambda item: item[0]["chunk_number"]
                )

        return grouped
    
    def _deduplicate_chunks(
        self,
        documents: list[str],
        metadatas: list[dict],
    ) -> tuple[list[str], list[dict]]:
        """
        Removes exact duplicate retrieved chunks while
        preserving retrieval order.
        """

        seen: set[tuple[str, int]] = set()

        unique_documents: list[str] = []
        unique_metadatas: list[dict] = []

        for metadata, document in zip(
            metadatas,
            documents,
        ):

            key = (
                metadata["filename"],
                metadata["chunk_number"],
            )

            if key in seen:
                continue

            seen.add(key)

            unique_documents.append(
                document,
            )

            unique_metadatas.append(
                metadata,
            )

        return (
            unique_documents,
            unique_metadatas,
        )

    def _build_document_header(
        self,
        filename: str,
    ) -> list[str]:

        if not self.config.include_document_headers:
            return []

        separator = self._separator()

        return [
            separator,
            f"SOURCE [{filename}]",
            separator,
            f"Document : {filename}",
            "",
        ]

    def _build_chunk_header(
        self,
        metadata: dict,
    ) -> list[str]:

        if not self.config.include_chunk_headers:
            return []

        lines: list[str] = []

        if self.config.include_chunk_numbers:
            lines.extend(
                [
                    (
                        f"Chunk    : "
                        f"{metadata['chunk_number']} / "
                        f"{metadata['total_chunks']}"
                    )
                ]
            )

        lines.extend(
            [
                "Content",
                "-------",
                "",
            ]
        )

        return lines

    def _build_chunk(
        self,
        metadata: dict,
        document: str,
    ) -> list[str]:
        """
        Builds one formatted evidence block.

        Formatting only.
        Budgeting is handled by build_context().
        """

        lines: list[str] = []

        lines.extend(
            self._build_chunk_header(
                metadata
            )
        )

        lines.append(
            document.strip()
        )

        lines.extend(
            [
                "",
                self._separator(),
                "",
            ]
        )

        return lines

    def _iter_document_sections(
        self,
        grouped: OrderedDict[
            str,
            list[tuple[dict, str]]
        ],
    ):
        """
        Yields each grouped document.

        Separated from formatting so diagnostics
        and future compression logic can reuse the
        same traversal.
        """

        for filename, chunks in grouped.items():
            yield filename, chunks

    def _build_document_section(
        self,
        filename: str,
        chunks: list[tuple[dict, str]],
    ) -> list[str]:
        """
        Builds one formatted document section.

        This method performs formatting only.

        Budgeting is intentionally handled inside
        build_context().
        """

        lines: list[str] = []

        lines.extend(
            self._build_document_header(
                filename
            )
        )

        for metadata, document in chunks:

            lines.extend(
                self._build_chunk(
                    metadata,
                    document,
                )
            )

        return lines

    def _estimate_section_size(
        self,
        lines: list[str],
    ) -> int:
        """
        Estimates the character cost of a formatted
        section after joining with newline characters.
        """

        return sum(
            len(line) + 1
            for line in lines
        )

    def _truncate_context(
        self,
        context: str,
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
        metadatas: list[dict],
    ) -> str:

        if not documents:
            return ""

        documents, metadatas = self._deduplicate_chunks(
            documents,
            metadatas,
        )

        #
        # Simple mode.
        #

        if not self.config.group_by_document:

            context = "\n\n".join(
                document.strip()
                for document in documents
            )

            return self._truncate_context(
                context
            )

        #
        # Evidence-oriented context.
        #

        remaining_budget = (
            self.config.max_context_characters
            if self.config.max_context_characters is not None
            else float("inf")
        )

        lines: list[str] = []

        source_id = 1

        for metadata, document in zip(
            metadatas,
            documents,
        ):

            separator = self._separator()

            evidence_block = [
                separator,
                f"SOURCE [{source_id}]",
                separator,
                f"Document : {metadata['filename']}",
                (
                    f"Chunk    : "
                    f"{metadata['chunk_number']} / "
                    f"{metadata['total_chunks']}"
                ),
                "",
                "Content",
                "-------",
                "",
                document.strip(),
                "",
            ]

            block_size = self._estimate_section_size(
                evidence_block
            )

            if block_size > remaining_budget:
                break

            lines.extend(
                evidence_block
            )

            remaining_budget -= block_size

            source_id += 1

        context = "\n".join(
            lines
        ).strip()

        return self._truncate_context(
            context
        )


context_builder = ContextBuilder()