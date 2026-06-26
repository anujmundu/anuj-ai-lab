from app.rag.vector_store import vector_store


class DuplicateDetector:

    def is_indexed(
        self,
        filename: str
    ) -> bool:

        results = vector_store.collection.get(
            where={
                "filename": filename
            }
        )

        return len(results["ids"]) > 0


duplicate_detector = DuplicateDetector()