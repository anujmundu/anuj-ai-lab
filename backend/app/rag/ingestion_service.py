from pathlib import Path

from app.rag.document_loader import document_loader
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

        # Store every chunk
        for index, chunk in enumerate(chunks, start=1):

            chunk_id = f"{filename}_chunk_{index:03d}"

            vector_store.add(
                chunk_id,
                chunk
            )

            chunk_ids.append(chunk_id)

        return {
            "filename": filename,
            "chunks_indexed": len(chunk_ids),
            "chunk_ids": chunk_ids
        }


ingestion_service = IngestionService()