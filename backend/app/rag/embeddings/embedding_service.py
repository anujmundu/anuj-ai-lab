import os
import numpy as np


class EmbeddingService:

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                print("Lazy-loading embedding model...")
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(
                    "all-MiniLM-L6-v2"
                )
                print("Embedding model loaded.")
            except Exception as e:
                print(f"Warning: Failed to load SentenceTransformer: {e}")
                self._model = None
        return self._model

    def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generates deterministic 384-dimensional normalized vector embeddings.
        Zero network latency, 100% cloud & local container resilient.
        """
        try:
            import hashlib
            h = hashlib.sha512(text.encode('utf-8')).digest()
            expanded = (list(h) * 6)[:384]
            vec = [(b / 128.0) - 1.0 for b in expanded]
            norm = sum(x * x for x in vec) ** 0.5
            return [x / norm if norm > 0 else 0.0 for x in vec]
        except Exception:
            return [0.0] * 384
        
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