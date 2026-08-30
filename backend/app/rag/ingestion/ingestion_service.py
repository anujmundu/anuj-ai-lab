from pathlib import Path

from app.rag.document_loader import document_loader
from app.rag.text_chunker import text_chunker
from app.rag.vector_store import vector_store
from app.rag.metadata import metadata_builder
from app.rag.duplicate_detector import duplicate_detector
from app.rag.parent_child import parent_child_builder
from app.rag.parent_child_metadata import (
    parent_child_metadata_builder,
)


class IngestionService:

    def ingest(
        self,
        file_path: str,
        original_filename: str | None = None,
    ) -> dict:

        filename = original_filename or Path(file_path).stem

        status = "indexed"

        if duplicate_detector.exists(filename):

            vector_store.delete_document(
                filename,
                sync_bm25=False,
            )

            status = "reindexed"

        text = document_loader.load(
            file_path,
        )

        # --------------------------------------------------
        # Knowledge Graph Entity & Relation Indexing
        # --------------------------------------------------
        try:
            from app.rag.graph.graph_retriever import graph_retriever
            graph_retriever.index_text(text)
        except Exception:
            pass

        # --------------------------------------------------
        # Existing chunking behavior.
        #
        # TextChunker remains completely unchanged.
        # --------------------------------------------------
        chunks = text_chunker.chunk(
            text,
        )

        total_chunks = len(chunks)

        # --------------------------------------------------
        # Build deterministic parent/child structure.
        #
        # Parent chunks are context objects.
        # Child chunks remain the retrieval/indexing units.
        # --------------------------------------------------

        parent_child_document = parent_child_builder.build(
            chunks,
            document_id=filename,
        )

        chunk_ids: list[str] = []

        for index, child in enumerate(
            parent_child_document.children,
            start=1,
        ):

            # --------------------------------------------------
            # Existing metadata remains the canonical source
            # for filename/chunk numbering/chunk_id/indexed_at.
            # --------------------------------------------------

            metadata = metadata_builder.build(
                filename,
                index,
                total_chunks,
            )

            # --------------------------------------------------
            # Add parent/child relationship metadata.
            #
            # IMPORTANT:
            # Existing chunk_id is preserved.
            # Existing vector-store IDs are therefore unchanged.
            # --------------------------------------------------

            parent_child_metadata = (
                parent_child_metadata_builder.build_child_metadata(
                    filename=filename,
                    chunk_number=index,
                    total_chunks=total_chunks,
                    child=child,
                )
            )

            metadata.update(
                {
                    "parent_id": parent_child_metadata[
                        "parent_id"
                    ],
                    "child_id": parent_child_metadata[
                        "child_id"
                    ],
                    "chunk_type": parent_child_metadata[
                        "chunk_type"
                    ],
                }
            )

            # --------------------------------------------------
            # Preserve the existing vector-store ID.
            # --------------------------------------------------

            vector_store.add(
                metadata["chunk_id"],
                child.text,
                metadata,
            )

            chunk_ids.append(
                metadata["chunk_id"],
            )

        # --------------------------------------------------
        # Rebuild BM25 once after the document has been
        # fully indexed.
        # --------------------------------------------------

        vector_store.sync_bm25_index()

        return {
            "filename": filename,
            "status": status,
            "chunks_indexed": total_chunks,
            "chunk_ids": chunk_ids,
        }


ingestion_service = IngestionService()