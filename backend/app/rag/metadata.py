from datetime import datetime, timezone


class MetadataBuilder:

    def build(
        self,
        filename: str,
        chunk_number: int,
        total_chunks: int
    ) -> dict:

        return {
            "filename": filename,
            "chunk_number": chunk_number,
            "total_chunks": total_chunks,
            "chunk_id": f"{filename}_chunk_{chunk_number:03d}",
            "indexed_at": datetime.now(timezone.utc).isoformat()
        }



metadata_builder = MetadataBuilder()