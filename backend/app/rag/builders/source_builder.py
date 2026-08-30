class SourceBuilder:

    def build(
        self,
        metadatas: list[dict],
    ) -> list[dict]:

        return [
            {
                "filename": metadata.get("filename", metadata.get("source", "Document")),
                "chunk_id": metadata.get("chunk_id", str(idx)),
                "chunk_number": metadata.get("chunk_number", idx + 1),
                "total_chunks": metadata.get("total_chunks", len(metadatas)),
            }
            for idx, metadata in enumerate(metadatas)
            if isinstance(metadata, dict)
        ]


source_builder = SourceBuilder()