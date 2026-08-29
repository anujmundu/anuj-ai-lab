from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParentChunk:
    """
    A larger context-bearing chunk.

    Parent chunks are not the primary vector retrieval units.
    They provide expanded context around retrieved child chunks.
    """

    parent_id: str

    text: str

    index: int


@dataclass(frozen=True, slots=True)
class ChildChunk:
    """
    A smaller retrieval-oriented chunk.

    Child chunks are the units that can be embedded and retrieved.
    Each child points back to its parent chunk.
    """

    child_id: str

    parent_id: str

    text: str

    index: int


@dataclass(frozen=True, slots=True)
class ParentChildDocument:
    """
    Parent-child representation of a document.

    The original document is represented by a deterministic
    collection of parent chunks and their child chunks.
    """

    parents: tuple[ParentChunk, ...]

    children: tuple[ChildChunk, ...]
    
class ParentChildBuilder:
    """
    Builds a deterministic parent-child hierarchy from
    existing flat text chunks.

    Existing TextChunker behavior is intentionally preserved.
    This component operates on the resulting list[str].
    """

    def __init__(
        self,
        *,
        children_per_parent: int = 3,
    ) -> None:

        if children_per_parent < 1:
            raise ValueError(
                "children_per_parent must be at least 1"
            )

        self.children_per_parent = children_per_parent

    def build(
        self,
        chunks: list[str],
        *,
        document_id: str,
    ) -> ParentChildDocument:

        if not document_id.strip():
            raise ValueError(
                "document_id must not be empty"
            )

        if not chunks:
            return ParentChildDocument(
                parents=(),
                children=(),
            )

        parents: list[ParentChunk] = []
        children: list[ChildChunk] = []

        for parent_index, start in enumerate(
            range(
                0,
                len(chunks),
                self.children_per_parent,
            )
        ):

            parent_chunks = chunks[
                start:start + self.children_per_parent
            ]

            parent_id = (
                f"{document_id}:parent:{parent_index}"
            )

            parent_text = " ".join(
                chunk.strip()
                for chunk in parent_chunks
                if chunk.strip()
            )

            parent = ParentChunk(
                parent_id=parent_id,
                text=parent_text,
                index=parent_index,
            )

            parents.append(parent)

            for local_index, chunk in enumerate(
                parent_chunks
            ):

                child_index = start + local_index

                child_id = (
                    f"{document_id}:child:{child_index}"
                )

                children.append(
                    ChildChunk(
                        child_id=child_id,
                        parent_id=parent_id,
                        text=chunk,
                        index=child_index,
                    )
                )

        return ParentChildDocument(
            parents=tuple(parents),
            children=tuple(children),
        )


parent_child_builder = ParentChildBuilder()