import re
import unicodedata

from app.rag.semantic_matcher_config import (
    SemanticMatcherConfig,
)
from app.rag.embedding_provider import EmbeddingProvider
from app.rag.ollama_embedding_provider import OllamaEmbeddingProvider


class SemanticMatcher:
    """
    Lightweight semantic comparison engine.

    Responsibilities
    ----------------

    • Normalize text
    • Tokenize text
    • Remove stopwords
    • Produce reusable lexical features

    Future responsibilities
    -----------------------

    • Lemmatization
    • Stemming
    • Embedding similarity
    • CrossEncoder scoring
    • NLI
    • Claim verification
    """

    def __init__(
        self,
        config: SemanticMatcherConfig | None = None,
    ):

        self.config = (
            config
            or SemanticMatcherConfig()
        )
        
        # ----------------------------------------------
        # Optional Embedding Provider
        # ----------------------------------------------

        self.embedding_provider: EmbeddingProvider | None = None

        if self.config.enable_embeddings:

            provider = (
                self.config.embedding_provider
                .strip()
                .lower()
            )

            if provider == "ollama":

                self.embedding_provider = (
                    OllamaEmbeddingProvider(
                        self.config,
                    )
                )

            else:

                raise ValueError(
                    f"Unsupported embedding provider: "
                    f"{self.config.embedding_provider}"
                )
        
        self._validate_weights()
    
    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------

    def _validate_weights(
        self,
    ) -> None:
        """
        Validate similarity weights.

        All weights should sum to 1.0.
        """

        total = (

            self.config.jaccard_weight

            + self.config.containment_weight

            + self.config.overlap_weight

            + self.config.sequence_weight

        )

        if abs(total - 1.0) > 1e-6:

            raise ValueError(

                "SemanticMatcher similarity weights "
                "must sum to 1.0."

            )
            
    def _embedding_similarity(
            self,
            text_a: str,
            text_b: str,
        ) -> float:
            """
            Compute embedding similarity if an embedding
            provider is configured.
            """

            if self.embedding_provider is None:
                return 0.0

            return self.embedding_provider.similarity(
                text_a,
                text_b,
            )
        
    # --------------------------------------------------
    # Normalization
    # --------------------------------------------------

    def normalize(
        self,
        text: str | None,
    ) -> str:

        if not self.config.enabled:
            return text or ""

        text = text or ""

        if self.config.normalize_unicode:

            text = unicodedata.normalize(
                "NFKC",
                text,
            )

        if self.config.lowercase:

            text = text.lower()

        if self.config.remove_punctuation:

            text = re.sub(
                r"[^\w\s]",
                " ",
                text,
            )

        if self.config.collapse_whitespace:

            text = re.sub(
                r"\s+",
                " ",
                text,
            )

        if self.config.strip_whitespace:

            text = text.strip()

        return text
    
    # --------------------------------------------------
    # Token normalization
    # --------------------------------------------------

    def _normalize_token(
        self,
        token: str,
    ) -> str:

        token = token.lower()

        suffixes = (
            "ations",
            "ation",
            "ments",
            "ment",
            "ingly",
            "edly",
            "ing",
            "ed",
            "es",
            "s",
        )

        for suffix in suffixes:

            if (
                len(token) > len(suffix) + 2
                and token.endswith(suffix)
            ):

                return token[:-len(suffix)]

        return token

    # --------------------------------------------------
    # Tokenization
    # --------------------------------------------------

    def tokenize(
        self,
        text: str | None,
    ) -> list[str]:

        normalized = self.normalize(
            text,
        )

        if not normalized:

            return []

        tokens = re.findall(
            r"\b\w+\b",
            normalized,
        )

        tokens = [

            self._normalize_token(token)

            for token in tokens

            if len(token)
            >= self.config.minimum_token_length

        ]

        if self.config.remove_stopwords:

            tokens = [

                token

                for token in tokens

                if token
                not in self.config.stopwords
            ]

        if self.config.remove_duplicate_tokens:

            tokens = list(
                dict.fromkeys(
                    tokens,
                )
            )

        return tokens

    # --------------------------------------------------
    # Keyword Extraction
    # --------------------------------------------------

    def extract_keywords(
        self,
        text: str,
    ) -> list[str]:
        """
        Current implementation simply returns
        normalized content tokens.

        Future versions may use:

        • TF-IDF
        • YAKE
        • KeyBERT
        • RAKE
        """

        return self.tokenize(
            text,
        )
        
    # --------------------------------------------------
    # Similarity Metrics
    # --------------------------------------------------

    @staticmethod
    def token_overlap(
        tokens_a: list[str],
        tokens_b: list[str],
    ) -> set[str]:
        """
        Compute shared tokens.
        """

        return set(tokens_a).intersection(
            tokens_b,
        )

    @staticmethod
    def jaccard_similarity(
        tokens_a: list[str],
        tokens_b: list[str],
    ) -> float:
        """
        Jaccard similarity.

        intersection / union
        """

        a = set(tokens_a)
        b = set(tokens_b)

        union = a.union(b)

        if not union:
            return 1.0

        return len(
            a.intersection(b)
        ) / len(union)

    @staticmethod
    def containment_score(
        tokens_a: list[str],
        tokens_b: list[str],
    ) -> float:
        """
        Percentage of tokens from A that
        appear in B.
        """

        if not tokens_a:
            return 1.0

        shared = len(
            set(tokens_a).intersection(
                tokens_b,
            )
        )

        return shared / len(
            set(tokens_a),
        )

    @staticmethod
    def overlap_coefficient(
        tokens_a: list[str],
        tokens_b: list[str],
    ) -> float:
        """
        Overlap coefficient.

        intersection /
        min(len(A), len(B))
        """

        a = set(tokens_a)
        b = set(tokens_b)

        if not a or not b:
            return 0.0

        shared = len(
            a.intersection(b),
        )

        return shared / min(
            len(a),
            len(b),
        )

    @staticmethod
    def sequence_similarity(
        text_a: str,
        text_b: str,
    ) -> float:
        """
        Character-level similarity.

        Useful for detecting near-identical
        sentences.
        """

        from difflib import SequenceMatcher

        return SequenceMatcher(
            None,
            text_a,
            text_b,
        ).ratio()
        
    # --------------------------------------------------
    # Score Calculation
    # --------------------------------------------------

    def _calculate_lexical_score(
        self,
        *,
        jaccard: float,
        containment: float,
        overlap: float,
        sequence: float,
    ) -> float:
        """
        Combine the lexical similarity metrics into a
        single weighted score.

        Embedding similarity will later be fused with
        this lexical score.
        """

        return (

            jaccard
            * self.config.jaccard_weight

            + containment
            * self.config.containment_weight

            + overlap
            * self.config.overlap_weight

            + sequence
            * self.config.sequence_weight

        )

    def confidence(
        self,
        score: float,
    ) -> dict:
        """
        Convert similarity score into a
        confidence label.
        """

        score = max(
            0.0,
            min(
                1.0,
                score,
            ),
        )

        if score >= self.config.high_similarity:

            label = "High"

        elif score >= self.config.medium_similarity:

            label = "Medium"

        elif score >= self.config.low_similarity:

            label = "Low"

        else:

            label = "Very Low"

        return {

            "score": round(
                score,
                3,
            ),

            "label": label,
        }
        
    # --------------------------------------------------
    # Comparison Engine
    # --------------------------------------------------

    def compare(
        self,
        text_a: str,
        text_b: str,
    ) -> dict:
        """
        Compare two pieces of text using
        multiple lexical similarity metrics.

        This serves as the common semantic
        comparison engine for:

        • Citation grounding
        • Hallucination detection
        • Retrieval diagnostics
        • Answer quality
        • Claim verification
        """
        # --------------------------------------------------
        # Normalization
        # --------------------------------------------------

        normalized_a = self.normalize(
            text_a,
        )

        normalized_b = self.normalize(
            text_b,
        )

        tokens_a = self.tokenize(
            normalized_a,
        )

        tokens_b = self.tokenize(
            normalized_b,
        )
        
        # --------------------------------------------------
        # Lexical Similarity
        # --------------------------------------------------

        shared = sorted(
            self.token_overlap(
                tokens_a,
                tokens_b,
            )
        )

        jaccard = self.jaccard_similarity(
            tokens_a,
            tokens_b,
        )

        containment = self.containment_score(
            tokens_a,
            tokens_b,
        )

        overlap = self.overlap_coefficient(
            tokens_a,
            tokens_b,
        )

        sequence = self.sequence_similarity(
            normalized_a,
            normalized_b,
        )
        
        # --------------------------------------------------
        # Embedding Similarity
        # --------------------------------------------------

        embedding_similarity = self._embedding_similarity(
            normalized_a,
            normalized_b,
        )
        
        # --------------------------------------------------
        # Score Fusion
        # --------------------------------------------------

        lexical_score = self._calculate_lexical_score(

            jaccard=jaccard,

            containment=containment,

            overlap=overlap,

            sequence=sequence,

        )

        overall = (

            self.config.lexical_weight
            * lexical_score

            +

            self.config.embedding_weight
            * embedding_similarity

        )
        
        # --------------------------------------------------
        # Diagnostics
        # --------------------------------------------------

        confidence = self.confidence(
            overall,
        )

        explanation = []

        if jaccard >= 0.80:

            explanation.append(
                "Strong lexical overlap"
            )

        elif jaccard >= 0.50:

            explanation.append(
                "Moderate lexical overlap"
            )

        else:

            explanation.append(
                "Weak lexical overlap"
            )

        if containment >= 0.80:

            explanation.append(
                "Most concepts are supported"
            )

        elif containment >= 0.50:

            explanation.append(
                "Partial concept support"
            )

        else:

            explanation.append(
                "Limited concept support"
            )

        if sequence >= 0.90:

            explanation.append(
                "Near-identical wording"
            )

        elif sequence >= 0.70:

            explanation.append(
                "Similar phrasing"
            )

        else:

            explanation.append(
                "Different wording"
            )

        return {

            "normalized": {

                "text_a": normalized_a,

                "text_b": normalized_b,
            },

            "tokens": {

                "text_a": tokens_a,

                "text_b": tokens_b,

                "shared": shared,
            },

            "metrics": {

                "jaccard": round(
                    jaccard,
                    3,
                ),

                "containment": round(
                    containment,
                    3,
                ),

                "overlap": round(
                    overlap,
                    3,
                ),

                "sequence": round(
                    sequence,
                    3,
                ),

                "lexical": round(
                    lexical_score,
                    3,
                ),

                "embedding": round(
                    embedding_similarity,
                    3,
                ),

                "overall": round(
                    overall,
                    3,
                ),
            },

            "confidence": confidence,

            "diagnostics": {
                
                "embedding_similarity": round(
                    embedding_similarity,
                    3,
                ),

                "shared_token_count": len(
                    shared,
                ),

                "token_count_a": len(
                    tokens_a,
                ),

                "token_count_b": len(
                    tokens_b,
                ),

                "shared_tokens": shared,
            },

            "explanation": explanation,
        }

    # --------------------------------------------------

    def compare_sentences(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> dict:
        """
        Convenience wrapper for sentence-level
        comparison.
        """

        return self.compare(
            sentence_a,
            sentence_b,
        )

    # --------------------------------------------------

    def compare_documents(
        self,
        document_a: str,
        document_b: str,
    ) -> dict:
        """
        Compare two longer documents.

        Current implementation performs a
        lexical comparison.

        Future versions may use embeddings,
        chunk alignment, or NLI.
        """

        return self.compare(
            document_a,
            document_b,
        )
        
    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    def diagnostics(
        self,
        text_a: str,
        text_b: str,
    ) -> dict:
        """
        Public diagnostics interface.

        Returns the complete comparison report.
        This wrapper exists so downstream modules
        don't need to know which comparison
        implementation is being used.
        """

        return self.compare(
            text_a,
            text_b,
        )

    # --------------------------------------------------
    # Batch Processing
    # --------------------------------------------------

    def compare_many(
        self,
        query: str,
        documents: list[str],
    ) -> list[dict]:
        """
        Compare one query against multiple
        candidate documents.

        Results are returned sorted by
        overall similarity.
        """

        results = []

        for index, document in enumerate(
            documents,
        ):

            result = self.compare(
                query,
                document,
            )

            result["document_index"] = index

            results.append(
                result,
            )

        results.sort(

            key=lambda item:
            item["metrics"]["overall"],

            reverse=True,
        )

        return results

    # --------------------------------------------------
    # Best Match
    # --------------------------------------------------

    def best_match(
        self,
        query: str,
        documents: list[str],
    ) -> dict | None:
        """
        Return the most similar document.

        Future versions may use embeddings,
        rerankers or NLI instead.
        """

        results = self.compare_many(
            query,
            documents,
        )

        if not results:

            return None

        return results[0]

    # --------------------------------------------------
    # Extension Hooks
    # --------------------------------------------------

    def embedding_similarity(
        self,
        *_,
        **__,
    ):
        """
        Placeholder.

        V2:
            Sentence Transformers

        V3:
            CrossEncoder

        V4:
            BGE
        """

        raise NotImplementedError(
            "Embedding similarity "
            "will be introduced in "
            "SemanticMatcher V2."
        )

    def natural_language_inference(
        self,
        *_,
        **__,
    ):
        """
        Placeholder.

        Future versions will support

        • Entailment

        • Contradiction

        • Neutral
        """

        raise NotImplementedError(
            "Natural Language "
            "Inference is planned "
            "for SemanticMatcher V3."
        )


semantic_matcher = SemanticMatcher()