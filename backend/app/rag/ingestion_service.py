from pathlib import Path

from app.rag.document_loader import document_loader
from app.rag.text_chunker import text_chunker
from app.rag.vector_store import vector_store
from app.rag.metadata import metadata_builder
from app.rag.duplicate_detector import duplicate_detector


class IngestionService:

    def ingest(
        self,
        file_path: str
    ) -> dict:

        filename = Path(file_path).stem

        status = "indexed"

        if duplicate_detector.exists(filename):

            vector_store.delete_document(
                filename,
                sync_bm25=False,
            )

            status = "reindexed"

        text = document_loader.load(file_path)

        chunks = text_chunker.chunk(text)

        chunk_ids = []

        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks, start=1):

            metadata = metadata_builder.build(
                filename,
                index,
                total_chunks
            )

            vector_store.add(
                metadata["chunk_id"],
                chunk,
                metadata
            )

            chunk_ids.append(
                metadata["chunk_id"]
            )

        # ------------------------------------------
        # Rebuild BM25 once after the document
        # has been fully indexed.
        # ------------------------------------------

        vector_store.sync_bm25_index()

        return {
            "filename": filename,
            "status": status,
            "chunks_indexed": total_chunks,
            "chunk_ids": chunk_ids
        }


ingestion_service = IngestionService()