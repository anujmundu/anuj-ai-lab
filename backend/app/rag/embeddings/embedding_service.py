from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:

    def __init__(self):

        print("Loading embedding model...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded.")

    def embed(
        self,
        text: str,
    ) -> list[float]:

        return self.model.encode(
            text
        ).tolist()
        
    def cosine_similarity(
        self,
        embedding_a: list[float],
        embedding_b: list[float],
    ) -> float:
        
        if len(embedding_a) != len(embedding_b):
            raise ValueError(
                "Embedding vectors must have the same length."
            )

        a = np.asarray(
            embedding_a,
            dtype=np.float32,
        )

        b = np.asarray(
            embedding_b,
            dtype=np.float32,
        )

        denominator = (
            np.linalg.norm(a)
            * np.linalg.norm(b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(a, b)
            / denominator
        )


embedding_service = EmbeddingService()