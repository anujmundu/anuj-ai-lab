from app.rag.retrieval_config import RetrievalConfig


class ResultFusion:
    """
    Combines retrieval results from multiple retrieval engines.

    Supports:

    • Weighted score fusion
    • Reciprocal Rank Fusion (RRF)
    • Duplicate removal
    • Score normalization

    Returns standard ChromaDB-style results along with
    retrieval diagnostics for debugging and evaluation.
    """

    def __init__(
        self,
        config: RetrievalConfig | None = None
    ):

        self.config = config or RetrievalConfig()

    # --------------------------------------------------
    # Score Normalization
    # --------------------------------------------------

    def _normalize_semantic_scores(
        self,
        results: dict,
    ) -> None:
        """
        Semantic scores are already converted into a
        bounded similarity score (0–1) inside _merge().

        Nothing to normalize here.
        """

        return

    def _normalize_keyword_scores(
        self,
        results: dict,
    ) -> None:
        """
        Normalize BM25 scores into the range [0, 1]
        using min-max normalization.
        """

        scores = results.get(
            "distances",
            [[]],
        )[0]

        if not scores:
            return

        maximum = max(scores)
        minimum = min(scores)

        if maximum == minimum:

            results["distances"][0] = [
                1.0
                for _ in scores
            ]

            return

        results["distances"][0] = [

            (
                score - minimum
            )
            /
            (
                maximum - minimum
            )

            for score in scores
        ]

    # --------------------------------------------------
    # Fusion
    # --------------------------------------------------

    def combine(
        self,
        semantic: dict | None,
        keyword: dict | None,
        k: int
    ) -> dict:

        if self.config.normalize_scores:

            if semantic:

                self._normalize_semantic_scores(
                    semantic,
                )

            if keyword:

                self._normalize_keyword_scores(
                    keyword,
                )

        merged: dict = {}

        if semantic and self.config.enable_semantic:

            self._merge(
                merged,
                semantic,
                source="semantic"
            )

        if keyword and self.config.enable_keyword:

            self._merge(
                merged,
                keyword,
                source="keyword"
            )

        items = sorted(
            merged.items(),
            key=lambda item: item[1]["combined_score"],
            reverse=True
        )[:k]

        return {
            "ids": [[
                item[0]
                for item in items
            ]],
            "documents": [[
                item[1]["document"]
                for item in items
            ]],
            "metadatas": [[
                item[1]["metadata"]
                for item in items
            ]],
            "distances": [[
                item[1]["distance"]
                for item in items
            ]],
            "retrieval": [[
                {
                    "semantic_score": item[1]["semantic_score"],
                    "keyword_score": item[1]["keyword_score"],
                    "combined_score": item[1]["combined_score"],
                    "semantic_rank": item[1]["semantic_rank"],
                    "keyword_rank": item[1]["keyword_rank"],
                }
                for item in items
            ]]
        }

    # --------------------------------------------------
    # Internal Merge
    # --------------------------------------------------

    def _merge(
        self,
        merged: dict,
        results: dict,
        source: str
    ):

        ids = results.get(
            "ids",
            [[]],
        )[0]

        documents = results.get(
            "documents",
            [[]],
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]],
        )[0]

        distances = results.get(
            "distances",
            [[]],
        )[0]

        for rank, (
            doc_id,
            document,
            metadata,
            value
        ) in enumerate(

            zip(
                ids,
                documents,
                metadatas,
                distances,
            ),

            start=1,
        ):

            rerank_scores = results.get(
                "rerank_scores",
                [[]],
            )[0]
            
            if source == "semantic":

                if rerank_scores:

                    semantic_score = rerank_scores[
                        rank - 1
                    ]

                else:

                    semantic_score = (
                        1.0
                        /
                        (
                            1.0 + value
                        )
                    )

                keyword_score = 0.0
                distance = value

                keyword_score = 0.0

                distance = value

            else:

                semantic_score = 0.0

                keyword_score = value

                distance = value

            if self.config.fusion_strategy == "weighted":

                combined = (
                    semantic_score
                    * self.config.semantic_weight
                    +
                    keyword_score
                    * self.config.keyword_weight
                )

            else:

                combined = (
                    1.0
                    /
                    (
                        self.config.rrf_k
                        + rank
                    )
                )

            if doc_id not in merged:

                merged[doc_id] = {
                    "document": document,
                    "metadata": metadata,
                    "distance": distance,
                    "semantic_score": semantic_score,
                    "keyword_score": keyword_score,
                    "combined_score": combined,
                    "semantic_rank": (
                        rank
                        if source == "semantic"
                        else None
                    ),
                    "keyword_rank": (
                        rank
                        if source == "keyword"
                        else None
                    ),
                }

            else:

                merged_doc = merged[doc_id]

                merged_doc["semantic_score"] = max(
                    merged_doc["semantic_score"],
                    semantic_score,
                )

                merged_doc["keyword_score"] = max(
                    merged_doc["keyword_score"],
                    keyword_score,
                )

                merged_doc["combined_score"] += combined

                if source == "semantic":

                    merged_doc["semantic_rank"] = rank

                else:

                    merged_doc["keyword_rank"] = rank


result_fusion = ResultFusion()