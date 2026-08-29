from __future__ import annotations

from app.rag.embedding_provider import EmbeddingProvider
from app.rag.embedding_service import embedding_service


class SentenceTransformerEmbeddingProvider(
    EmbeddingProvider,
):
    """
    Embedding provider backed by the shared
    SentenceTransformer embedding service.

    Uses the same embedding model as the
    VectorStore so document and query
    embeddings are always compatible.
    """

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        return embedding_service.embed(
            text,
        )

    @staticmethod
    def cosine_similarity(
        embedding_a: list[float],
        embedding_b: list[float],
    ) -> float:

        if (
            len(embedding_a)
            != len(embedding_b)
        ):
            raise ValueError(
                "Embedding vectors must have the same length."
            )

        dot = sum(
            a * b
            for a, b in zip(
                embedding_a,
                embedding_b,
            )
        )

        norm_a = sum(
            a * a
            for a in embedding_a
        ) ** 0.5

        norm_b = sum(
            b * b
            for b in embedding_b
        ) ** 0.5

        if (
            norm_a == 0
            or norm_b == 0
        ):
            return 0.0

        return dot / (
            norm_a * norm_b
        )
        
    @property
    def provider_name(
        self,
    ) -> str:

        return "SentenceTransformer"


    @property
    def model_name(
        self,
    ) -> str:

        return "all-MiniLM-L6-v2"