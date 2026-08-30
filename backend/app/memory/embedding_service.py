from __future__ import annotations
import numpy as np


class MemoryEmbeddingService:
    """
    Generates embeddings for persistent memories with lazy loading.
    """

    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            try:
                print("Lazy-loading memory embedding model...")
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(
                    "all-MiniLM-L6-v2",
                )
                print("Memory embedding model loaded.")
            except Exception as e:
                print(f"Warning: Failed to load Memory SentenceTransformer: {e}")
                self._model = None
        return self._model

    def embed(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding vector for text.
        """
        if self.model is not None:
            return self.model.encode(
                text,
                normalize_embeddings=True,
            ).tolist()
        
        # Fast memory-safe fallback embedding (384 dimensions)
        import hashlib
        h = hashlib.sha256(text.encode('utf-8')).digest()
        base = [(b / 255.0) * 2 - 1 for b in h]
        vec = (base * 12)[:384]
        norm = sum(x * x for x in vec) ** 0.5
        return [x / norm if norm > 0 else 0.0 for x in vec]


memory_embedding_service = (
    MemoryEmbeddingService()
)