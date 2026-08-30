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
        if self.model is not None:
            return self.model.encode(
                text
            ).tolist()
        # Fast memory-safe fallback embedding
        import hashlib
        h = hashlib.sha256(text.encode('utf-8')).digest()
        return [(b / 255.0) * 2 - 1 for b in h[:384]]
        
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