class SourceBuilder:

    def build(
        self,
        metadatas: list[dict],
    ) -> list[dict]:

        return [
            {
                "filename": metadata["filename"],
                "chunk_id": metadata["chunk_id"],
                "chunk_number": metadata["chunk_number"],
                "total_chunks": metadata["total_chunks"],
            }
            for metadata in metadatas
        ]


source_builder = SourceBuilder()