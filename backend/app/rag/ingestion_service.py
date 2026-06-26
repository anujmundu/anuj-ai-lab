from pathlib import Path

from app.rag.document_loader import document_loader
from app.rag.metadata import metadata_builder
from app.rag.text_chunker import text_chunker
from app.rag.vector_store import vector_store


class IngestionService:

    def ingest(
        self,
        file_path: str
    ) -> dict:

        # Load document
        text = document_loader.load(file_path)

        # Split into chunks
        chunks = text_chunker.chunk(text)

        # Get filename without extension
        filename = Path(file_path).stem

        chunk_ids = []

        total_chunks = len(chunks)

        # Store every chunk
        for index, chunk in enumerate(chunks, start=1):

            metadata = metadata_builder.build(
                filename=filename,
                chunk_number=index,
                total_chunks=total_chunks
            )

            chunk_id = metadata["chunk_id"]

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