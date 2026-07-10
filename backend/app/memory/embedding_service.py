from sentence_transformers import SentenceTransformer


class MemoryEmbeddingService:
    """
    Generates embeddings for persistent memories.

    Responsibilities

    • Load the embedding model once.
    • Encode memory text.
    • Encode search queries.

    This service is intentionally independent of
    databases and retrieval logic.
    """

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2",
        )

    def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding vector for text.
        """

        return self.model.encode(
            text,
            normalize_embeddings=True,
        ).tolist()


memory_embedding_service = (
    MemoryEmbeddingService()
)