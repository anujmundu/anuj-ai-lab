import re
from collections import defaultdict

from app.rag.retrieval_config import RetrievalConfig


class RetrievalFilter:
    """
    Post-processes fused retrieval results.

    Current responsibilities

    • semantic threshold
    • max chunks per document
    • duplicate removal
    • document diversification

    Future responsibilities

    • embedding-based duplicate removal
    • MMR
    • metadata-aware filtering
    • context-aware filtering

    The public retrieval API remains unchanged.
    Additional diagnostics are returned under
    results["diagnostics"].
    """

    def __init__(
        self,
        config: RetrievalConfig | None = None
    ):

        self.config = config or RetrievalConfig()

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _tokenize(
        self,
        text: str
    ) -> set[str]:

        return set(
            re.findall(
                r"\w+",
                text.lower()
            )
        )

    def _jaccard_similarity(
        self,
        text_a: str,
        text_b: str
    ) -> float:

        tokens_a = self._tokenize(text_a)
        tokens_b = self._tokenize(text_b)

        union = tokens_a | tokens_b

        if not union:
            return 0.0

        return len(tokens_a & tokens_b) / len(union)

    def _passes_threshold(
        self,
        scores: dict
    ) -> bool:
        """
        Apply retrieval thresholds based on the active
        retrieval strategy.

        Semantic and Hybrid retrieval require a minimum
        semantic similarity score.

        Keyword retrieval currently performs no thresholding,
        since BM25 already returns ranked lexical matches.
        """

        strategy = self.config.retrieval_strategy

        if strategy == "keyword":
            return True

        return (
            scores.get(
                "semantic_score",
                0.0
            )
            >= self.config.min_semantic_score
        )

    def _is_duplicate(
        self,
        candidate: str,
        accepted: list[str]
    ) -> bool:

        if not self.config.remove_near_duplicates:
            return False

        for existing in accepted:

            similarity = self._jaccard_similarity(
                candidate,
                existing
            )

            if (
                similarity
                >= self.config.duplicate_similarity_threshold
            ):
                return True

        return False

    def _passes_diversification(
        self,
        metadata: dict,
        scores: dict,
        document_counts: dict
    ) -> bool:

        #
        # Future-proof signature.
        #
        # Today we only use the filename.
        # Future versions may use:
        #
        # • metadata
        # • retrieval scores
        # • semantic diversity
        # • timestamps
        # • document type
        #

        if not self.config.diversify_documents:
            return True

        filename = metadata["filename"]

        return document_counts[filename] == 0

    def _passes_document_limit(
        self,
        filename: str,
        document_counts: dict
    ) -> bool:

        return (
            document_counts[filename]
            < self.config.max_chunks_per_document
        )

    # --------------------------------------------------
    # Main Pipeline
    # --------------------------------------------------

    def apply(
        self,
        results: dict,
        k: int
    ) -> dict:

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        retrieval = results.get("retrieval", [[]])[0]

        filtered_ids = []
        filtered_documents = []
        filtered_metadatas = []
        filtered_distances = []
        filtered_retrieval = []

        accepted_documents: list[str] = []

        diagnostics = []

        document_counts = defaultdict(int)

        for (
            doc_id,
            document,
            metadata,
            distance,
            scores
        ) in zip(
            ids,
            documents,
            metadatas,
            distances,
            retrieval
        ):

            filename = metadata["filename"]

            # ------------------------------
            # Threshold
            # ------------------------------

            if not self._passes_threshold(
                scores
            ):

                diagnostics.append(
                    {
                        "chunk_id": doc_id,
                        "filename": filename,
                        "status": "FILTERED",
                        "reason": (
                            "LOW_SEMANTIC_SCORE"
                            if self.config.retrieval_strategy != "keyword"
                            else "LOW_RETRIEVAL_SCORE"
                        )
                    }
                )

                continue

            # ------------------------------
            # Duplicate Removal
            # ------------------------------

            if self._is_duplicate(
                document,
                accepted_documents
            ):

                diagnostics.append(
                    {
                        "chunk_id": doc_id,
                        "filename": filename,
                        "status": "FILTERED",
                        "reason": "DUPLICATE"
                    }
                )

                continue

            # ------------------------------
            # Diversification
            # ------------------------------

            if not self._passes_diversification(
                metadata,
                scores,
                document_counts
            ):

                diagnostics.append(
                    {
                        "chunk_id": doc_id,
                        "filename": filename,
                        "status": "FILTERED",
                        "reason": "DOCUMENT_DIVERSIFICATION"
                    }
                )

                continue

            # ------------------------------
            # Per-document limit
            # ------------------------------

            if not self._passes_document_limit(
                filename,
                document_counts
            ):

                diagnostics.append(
                    {
                        "chunk_id": doc_id,
                        "filename": filename,
                        "status": "FILTERED",
                        "reason": "MAX_CHUNKS_PER_DOCUMENT"
                    }
                )

                continue

            document_counts[filename] += 1

            accepted_documents.append(
                document
            )

            filtered_ids.append(doc_id)
            filtered_documents.append(document)
            filtered_metadatas.append(metadata)
            filtered_distances.append(distance)
            filtered_retrieval.append(scores)

            diagnostics.append(
                {
                    "chunk_id": doc_id,
                    "filename": filename,
                    "status": "KEPT",
                    "reason": "KEPT"
                }
            )

        #
        # Top-K is intentionally applied
        # after every filtering stage.
        #

        filtered_ids = filtered_ids[:k]
        filtered_documents = filtered_documents[:k]
        filtered_metadatas = filtered_metadatas[:k]
        filtered_distances = filtered_distances[:k]
        filtered_retrieval = filtered_retrieval[:k]

        return {
            "ids": [filtered_ids],
            "documents": [filtered_documents],
            "metadatas": [filtered_metadatas],
            "distances": [filtered_distances],
            "retrieval": [filtered_retrieval],
            "diagnostics": diagnostics
        }


retrieval_filter = RetrievalFilter()