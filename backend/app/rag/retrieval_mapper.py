from app.rag.retrieval_models import (
    RetrievalMetadata,
    RetrievalResult,
    RetrievalScores,
)


class RetrievalMapper:
    """
    Maps raw retrieval engine responses into the
    canonical RetrievalResult domain model.

    This isolates the rest of the RAG pipeline from
    ChromaDB's response format.
    """

    def build(
        self,
        results: dict,
    ) -> list[RetrievalResult]:

        ids = results.get("ids") or [[]]
        documents = results.get("documents") or [[]]
        metadatas = results.get("metadatas") or [[]]
        distances = results.get("distances") or [[]]

        retrieval_results: list[RetrievalResult] = []

        for (
            doc_id,
            document,
            metadata,
            distance,
        ) in zip(
            ids[0],
            documents[0],
            metadatas[0],
            distances[0],
        ):

            metadata = metadata or {}

            retrieval_metadata = RetrievalMetadata(
                filename=metadata.get("filename", ""),
                chunk_id=metadata.get("chunk_id", doc_id),
                chunk_number=metadata.get("chunk_number", 0),
                total_chunks=metadata.get("total_chunks", 0),
                source=metadata.get("source", ""),
            )

            similarity = 1.0 - float(distance)

            retrieval_scores = RetrievalScores(
                semantic_score=similarity,
                keyword_score=0.0,
                combined_score=similarity,
            )

            retrieval_results.append(
                RetrievalResult(
                    doc_id=doc_id,
                    document=document,
                    metadata=retrieval_metadata,
                    scores=retrieval_scores,
                )
            )

        return retrieval_results


retrieval_mapper = RetrievalMapper()