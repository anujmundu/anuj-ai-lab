from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """
    Base interface for all embedding providers.

    Every embedding backend (Ollama, SentenceTransformers,
    OpenAI, etc.) should inherit from this class.

    SemanticMatcher depends only on this interface,
    allowing embedding implementations to be swapped
    without modifying the matcher.
    """

    # --------------------------------------------------
    # Provider Metadata
    # --------------------------------------------------

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Human-readable provider name.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Human-readable embedding model name.
        """
        raise NotImplementedError

    # --------------------------------------------------
    # Embeddings
    # --------------------------------------------------

    @abstractmethod
    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding vector for a single piece
        of text.
        """
        raise NotImplementedError

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Providers may override this with a more efficient
        batch implementation.
        """

        return [
            self.embed_text(text)
            for text in texts
        ]

    # --------------------------------------------------
    # Similarity
    # --------------------------------------------------

    @abstractmethod
    def cosine_similarity(
        self,
        embedding_a: list[float],
        embedding_b: list[float],
    ) -> float:
        """
        Compute cosine similarity between two embedding
        vectors.
        """
        raise NotImplementedError

    def similarity(
        self,
        text_a: str,
        text_b: str,
    ) -> float:
        """
        Convenience helper that embeds two texts and
        computes their cosine similarity.

        The concrete provider is responsible for any
        caching performed inside embed_text().
        """

        embedding_a = self.embed_text(text_a)
        embedding_b = self.embed_text(text_b)

        return self.cosine_similarity(
            embedding_a,
            embedding_b,
        )

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    def diagnostics(self) -> dict:
        """
        Provider metadata exposed to diagnostics.
        """

        return {
            "provider": self.provider_name,
            "model": self.model_name,
        }