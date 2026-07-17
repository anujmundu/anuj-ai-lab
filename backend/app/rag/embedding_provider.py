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

        Returns 0.0 when either text cannot produce a
        meaningful embedding.
        """

        #
        # Guard against None
        #

        text_a = "" if text_a is None else text_a
        text_b = "" if text_b is None else text_b

        #
        # Remove surrounding whitespace
        #

        text_a = text_a.strip()
        text_b = text_b.strip()

        #
        # Empty text has no semantic similarity.
        #

        if not text_a or not text_b:
            return 0.0

        embedding_a = self.embed_text(text_a)
        embedding_b = self.embed_text(text_b)

        #
        # Defensive check.
        #

        if not embedding_a or not embedding_b:
            return 0.0

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