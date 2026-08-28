from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CachedEntry:
    query: str
    embedding: list[float]
    response: Any
    created_at: float = field(default_factory=time.time)
    ttl_seconds: float = 3600.0  # 1 hour default TTL
    hit_count: int = 0

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds


class SemanticCache:
    """
    Multi-tiered semantic cache for query embeddings and retrieval responses.
    Uses cosine similarity against cached query vectors to return instant hits.
    """

    def __init__(self, similarity_threshold: float = 0.95, max_entries: int = 1000) -> None:
        self.similarity_threshold = similarity_threshold
        self.max_entries = max_entries
        self._cache: list[CachedEntry] = []
        self._hits: int = 0
        self._misses: int = 0

    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def get(self, query: str, query_embedding: list[float] | None = None) -> Any | None:
        """Lookup by exact string match first, then by semantic embedding similarity."""
        # 1. Exact string match
        for entry in self._cache:
            if entry.is_expired():
                continue
            if entry.query.strip().lower() == query.strip().lower():
                entry.hit_count += 1
                self._hits += 1
                return entry.response

        # 2. Semantic vector match
        if query_embedding:
            best_similarity = 0.0
            best_entry: CachedEntry | None = None
            for entry in self._cache:
                if entry.is_expired() or not entry.embedding:
                    continue
                sim = self._cosine_similarity(query_embedding, entry.embedding)
                if sim > best_similarity:
                    best_similarity = sim
                    best_entry = entry

            if best_entry and best_similarity >= self.similarity_threshold:
                best_entry.hit_count += 1
                self._hits += 1
                return best_entry.response

        self._misses += 1
        return None

    def set(
        self,
        query: str,
        response: Any,
        embedding: list[float] | None = None,
        ttl_seconds: float = 3600.0,
    ) -> None:
        """Cache a query response with optional vector embedding and TTL."""
        # Evict expired or LRU entries if capacity reached
        if len(self._cache) >= self.max_entries:
            self._cache = [e for e in self._cache if not e.is_expired()]
            if len(self._cache) >= self.max_entries:
                # Evict lowest hit count entry
                self._cache.sort(key=lambda x: x.hit_count)
                self._cache.pop(0)

        entry = CachedEntry(
            query=query,
            embedding=embedding or [],
            response=response,
            ttl_seconds=ttl_seconds,
        )
        self._cache.append(entry)

    def get_stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        hit_rate = round(self._hits / total, 3) if total > 0 else 0.0
        return {
            "total_entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "max_entries": self.max_entries,
            "similarity_threshold": self.similarity_threshold,
        }

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0


semantic_cache = SemanticCache()
