from __future__ import annotations

import math
from typing import Any

import requests

from app.rag.embedding_provider import EmbeddingProvider
from app.rag.semantic_matcher_config import SemanticMatcherConfig


class OllamaEmbeddingProvider(EmbeddingProvider):
    """
    Embedding provider backed by a local Ollama server.

    Responsibilities
    ----------------
    • Generate embeddings
    • Cache embeddings
    • Compute cosine similarity
    • Expose provider diagnostics

    It deliberately contains no SemanticMatcher logic.
    """

    def __init__(
        self,
        config: SemanticMatcherConfig,
    ) -> None:

        self.config = config

        self.base_url = getattr(
            config,
            "ollama_base_url",
            "http://localhost:11434",
        )

        self._embedding_cache: dict[str, list[float]] = {}

        self._cache_hits = 0
        self._cache_misses = 0

    # --------------------------------------------------
    # Internal Helpers
    # --------------------------------------------------

    def _request_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Request an embedding from Ollama and validate
        the returned payload.
        """
        
        #
        # Empty or whitespace-only text cannot be embedded.
        #
        # Return an empty vector so the caller can decide
        # how to handle missing semantic information.
        #

        if not text:
            return []

        text = text.strip()

        if not text:
            return []

        try:

            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model_name,
                    "prompt": text,
                },
                timeout=60,
            )

            response.raise_for_status()

        except requests.RequestException as exc:

            raise ConnectionError(
                f"Failed to obtain embedding from Ollama "
                f"({self.base_url})."
            ) from exc

        payload = response.json()

        if not isinstance(payload, dict):

            raise TypeError(
                "Ollama response must be a JSON object."
            )

        if "embedding" not in payload:

            raise ValueError(
                "Ollama response does not contain an "
                "'embedding' field."
            )

        embedding = payload["embedding"]

        if not isinstance(embedding, list):

            raise TypeError(
                "Embedding must be returned as a list."
            )

        if len(embedding) == 0:

            raise RuntimeError(
                "Ollama returned an empty embedding for a non-empty input."
            )

        for index, value in enumerate(embedding):

            if not isinstance(value, (int, float)):

                raise TypeError(
                    f"Embedding element at index "
                    f"{index} is not numeric."
                )

        return embedding

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def _validate_embeddings(
        self,
        embedding_a: list[float],
        embedding_b: list[float],
    ) -> tuple[float, float]:
        """
        Validate embeddings and return their norms.
        """

        if len(embedding_a) != len(embedding_b):

            raise ValueError(
                "Embedding vectors must have the same length."
            )

        if not embedding_a:

            raise ValueError(
                "Embedding vectors cannot be empty."
            )

        norm_a = math.sqrt(
            sum(value * value for value in embedding_a)
        )

        norm_b = math.sqrt(
            sum(value * value for value in embedding_b)
        )

        if norm_a == 0:

            raise ValueError(
                "First embedding has zero magnitude."
            )

        if norm_b == 0:

            raise ValueError(
                "Second embedding has zero magnitude."
            )

        return norm_a, norm_b

    def _compute_cosine_similarity(
        self,
        embedding_a: list[float],
        embedding_b: list[float],
        norm_a: float,
        norm_b: float,
    ) -> float:
        """
        Compute cosine similarity between two validated
        embedding vectors.
        """

        dot = sum(
            a * b
            for a, b in zip(
                embedding_a,
                embedding_b,
            )
        )

        similarity = dot / (norm_a * norm_b)

        return max(
            0.0,
            min(
                1.0,
                similarity,
            ),
        )

    # --------------------------------------------------
    # Provider Metadata
    # --------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self.config.embedding_model

    # --------------------------------------------------
    # Embeddings
    # --------------------------------------------------

    def embed_text(
        self,
        text: str,
    ) -> list[float]:

        if self.config.cache_embeddings:

            cached = self._embedding_cache.get(text)

            if cached is not None:

                self._cache_hits += 1

                return cached

        self._cache_misses += 1

        embedding = self._request_embedding(text)

        if self.config.cache_embeddings:

            self._embedding_cache[text] = embedding

        return embedding

    def embed_texts(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Currently reuses the single-text implementation.
        This can later be replaced with a batch endpoint
        without affecting callers.
        """

        return [
            self.embed_text(text)
            for text in texts
        ]

    # --------------------------------------------------
    # Similarity
    # --------------------------------------------------

    def cosine_similarity(
        self,
        embedding_a: list[float],
        embedding_b: list[float],
    ) -> float:

        norm_a, norm_b = self._validate_embeddings(
            embedding_a,
            embedding_b,
        )

        return self._compute_cosine_similarity(
            embedding_a,
            embedding_b,
            norm_a,
            norm_b,
        )

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    def diagnostics(self) -> dict:

        diagnostics = super().diagnostics()

        diagnostics.update(
            {
                "endpoint": self.base_url,
                "cache_enabled": self.config.cache_embeddings,
                "cache_size": len(self._embedding_cache),
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
            }
        )

        return diagnostics