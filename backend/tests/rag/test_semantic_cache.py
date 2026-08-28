import time
from app.rag.cache.semantic_cache import SemanticCache


def test_semantic_cache_exact_match():
    cache = SemanticCache()
    cache.set("What is ChromaDB?", "ChromaDB is an open-source vector database.")

    hit = cache.get("what is chromadb?")
    assert hit == "ChromaDB is an open-source vector database."
    assert cache.get_stats()["hits"] == 1


def test_semantic_cache_semantic_similarity_hit():
    cache = SemanticCache(similarity_threshold=0.90)
    # Vectors with high similarity
    vec1 = [0.1, 0.2, 0.9, 0.1]
    vec2 = [0.11, 0.19, 0.89, 0.1]  # ~0.999 cosine similarity

    cache.set("Configure hybrid retrieval", "Hybrid retrieval merges BM25 and dense vector search.", embedding=vec1)

    hit = cache.get("Setup hybrid search", query_embedding=vec2)
    assert hit == "Hybrid retrieval merges BM25 and dense vector search."
    assert cache.get_stats()["hits"] == 1


def test_semantic_cache_miss_and_ttl():
    cache = SemanticCache()
    # Non-existent query
    assert cache.get("Unknown query") is None
    assert cache.get_stats()["misses"] == 1

    # TTL expired entry
    cache.set("Temporary data", "Value", ttl_seconds=0.01)
    time.sleep(0.02)
    assert cache.get("Temporary data") is None


def test_semantic_cache_eviction_and_clear():
    cache = SemanticCache(max_entries=2)
    cache.set("q1", "ans1")
    cache.set("q2", "ans2")
    cache.set("q3", "ans3")  # Triggers eviction

    assert len(cache._cache) == 2
    cache.clear()
    assert len(cache._cache) == 0
    assert cache.get_stats()["total_entries"] == 0
