from dataclasses import dataclass, field


@dataclass(slots=True)
class SemanticMatcherConfig:
    """
    Configuration for SemanticMatcher.

    This module provides lightweight lexical
    similarity for diagnostics.

    Future versions may replace or augment these
    metrics with embedding-based similarity while
    preserving the public API.
    """

    # --------------------------------------------------
    # Engine
    # --------------------------------------------------

    enabled: bool = True

    # --------------------------------------------------
    # Text normalization
    # --------------------------------------------------

    lowercase: bool = True

    strip_whitespace: bool = True

    collapse_whitespace: bool = True

    remove_punctuation: bool = True

    normalize_unicode: bool = True

    # --------------------------------------------------
    # Tokenization
    # --------------------------------------------------

    minimum_token_length: int = 2

    remove_duplicate_tokens: bool = False

    remove_stopwords: bool = True

    # --------------------------------------------------
    # Confidence thresholds
    # --------------------------------------------------

    high_similarity: float = 0.85

    medium_similarity: float = 0.65

    low_similarity: float = 0.40
    
    # --------------------------------------------------
    # Embedding Similarity (V2)
    # --------------------------------------------------

    enable_embeddings: bool = True

    embedding_provider: str = "ollama"
    
    ollama_base_url: str = "http://localhost:11434"

    embedding_model: str = "nomic-embed-text"

    cache_embeddings: bool = True
    
    # --------------------------------------------------
    # Similarity Weights
    # --------------------------------------------------

    jaccard_weight = 0.15

    containment_weight = 0.40

    overlap_weight = 0.35

    sequence_weight = 0.10
    
    # --------------------------------------------------
    # Hybrid Score Fusion (V2)
    # --------------------------------------------------

    lexical_weight: float = 0.40

    embedding_weight: float = 0.60

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    include_embedding_scores: bool = True

    include_normalized_text: bool = True

    include_tokens: bool = True

    include_metrics: bool = True

    include_explanations: bool = True

    # --------------------------------------------------
    # Stopwords
    # --------------------------------------------------

    stopwords: set[str] = field(
        default_factory=lambda: {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "been",
            "being",
            "by",
            "for",
            "from",
            "has",
            "have",
            "had",
            "he",
            "her",
            "his",
            "i",
            "if",
            "in",
            "into",
            "is",
            "it",
            "its",
            "of",
            "on",
            "or",
            "our",
            "she",
            "that",
            "the",
            "their",
            "them",
            "there",
            "these",
            "they",
            "this",
            "those",
            "to",
            "was",
            "were",
            "will",
            "with",
            "you",
            "your",
        }
    )