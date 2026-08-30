from app.rag.vector_store import vector_store


class DuplicateDetector:

    def exists(
        self,
        filename: str
    ) -> bool:

        results = vector_store.get_document_chunks(
            filename
        )

        return len(results["ids"]) > 0


duplicate_detector = DuplicateDetector()