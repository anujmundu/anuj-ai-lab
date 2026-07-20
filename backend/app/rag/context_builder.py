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
            f"Document: {filename}.txt",
            separator,
            "",
        ]

    def _build_chunk_header(
        self,
        metadata: dict,
    ) -> list[str]:

        if not self.config.include_chunk_headers:
            return []

        if self.config.include_chunk_numbers:

            title = (
                f"Chunk {metadata['chunk_number']} / "
                f"{metadata['total_chunks']}"
            )

        else:

            title = "Chunk"

        return [
            title,
            "",
        ]

    def _build_chunk(
        self,
        metadata: dict,
        document: str,
    ) -> list[str]:
        """
        Builds one formatted retrieved chunk.

        This helper performs formatting only.
        Budgeting is handled later by build_context().
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

        lines.append("")
        lines.append("-" * 50)
        lines.append("")

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
        
        documents, metadatas = (
            self._deduplicate_chunks(
                documents,
                metadatas,
            )
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

        grouped = self._group_by_document(
            documents,
            metadatas,
        )

        #
        # Character budget.
        #
        # None means unlimited.
        #

        remaining_budget = (
            self.config.max_context_characters
            if self.config.max_context_characters is not None
            else float("inf")
        )

        lines: list[str] = []

        first_document = True

        #
        # Chunk-level budgeting.
        #
        # We preserve retrieval ranking while still
        # grouping chunks under their document.
        #

        for filename, chunks in self._iter_document_sections(
            grouped
        ):

            document_header = self._build_document_header(
                filename
            )

            header_added = False

            for metadata, document in chunks:

                chunk_lines = self._build_chunk(
                    metadata,
                    document,
                )

                #
                # Estimate the entire chunk cost.
                #

                chunk_size = self._estimate_section_size(
                    chunk_lines
                )

                #
                # First chunk of a document also
                # requires the document header.
                #

                if not header_added:

                    header_size = self._estimate_section_size(
                        document_header
                    )

                    required = (
                        header_size +
                        chunk_size
                    )

                else:

                    required = chunk_size

                #
                # Budget exhausted.
                #

                if required > remaining_budget:
                    break

                #
                # Add spacing between documents.
                #

                if (
                    not first_document
                    and header_added is False
                ):

                    lines.append("")
                    remaining_budget -= 1

                #
                # Add document header once.
                #

                if not header_added:

                    lines.extend(
                        document_header
                    )

                    remaining_budget -= (
                        header_size
                    )

                    header_added = True

                    first_document = False

                #
                # Add chunk.
                #

                lines.extend(
                    chunk_lines
                )

                remaining_budget -= (
                    chunk_size
                )

            #
            # Global budget exhausted.
            #

            if remaining_budget <= 0:
                break

        context = "\n".join(
            lines
        ).strip()

        #
        # Defensive safeguard.
        #

        return self._truncate_context(
            context
        )


context_builder = ContextBuilder()