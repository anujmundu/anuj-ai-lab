from __future__ import annotations

from app.rag.parent_child import (
    ChildChunk,
    ParentChunk,
)


class ParentChildMetadataBuilder:
    """
    Builds metadata for parent/child chunks.

    Existing retrieval metadata fields are preserved.
    Parent/child identifiers are additive.
    """

    def build_child_metadata(
        self,
        *,
        filename: str,
        chunk_number: int,
        total_chunks: int,
        child: ChildChunk,
    ) -> dict:
        """
        Build metadata for a child chunk.

        Child chunks are the units that will be indexed
        and retrieved by the existing vector store.
        """

        return {
            "filename": filename,
            "chunk_number": chunk_number,
            "total_chunks": total_chunks,
            "chunk_id": child.child_id,
            "child_id": child.child_id,
            "parent_id": child.parent_id,
            "chunk_type": "child",
        }

    def build_parent_metadata(
        self,
        *,
        filename: str,
        parent: ParentChunk,
    ) -> dict:
        """
        Build metadata describing a parent chunk.

        Parents are currently context-bearing objects and
        are not independently indexed.
        """

        return {
            "filename": filename,
            "parent_id": parent.parent_id,
            "chunk_type": "parent",
            "parent_index": parent.index,
        }


parent_child_metadata_builder = ParentChildMetadataBuilder()