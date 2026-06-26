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

        # Prevent duplicate indexing
        if duplicate_detector.is_indexed(filename):
            return {
                "filename": filename,
                "status": "already_indexed"
            }

        text = document_loader.load(file_path)

        chunks = text_chunker.chunk(text)

        chunk_ids = []

        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks, start=1):

            chunk_id = f"{filename}_chunk_{index:03d}"

            metadata = metadata_builder.build(
                filename=filename,
                chunk_number=index,
                total_chunks=total_chunks
            )

            vector_store.add(
                doc_id=chunk_id,
                text=chunk,
                metadata=metadata
            )

            chunk_ids.append(chunk_id)

        return {
            "filename": filename,
            "chunks_indexed": len(chunk_ids),
            "chunk_ids": chunk_ids
        }


ingestion_service = IngestionService()