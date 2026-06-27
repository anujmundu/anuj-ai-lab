from app.rag.retrieval_config import RetrievalConfig


class ResultFusion:
    """
    Combines retrieval results from multiple retrieval engines.

    The current implementation performs:

    • Duplicate removal
    • Weighted preference
    • Top-k limiting

    Future versions may implement:

    • Reciprocal Rank Fusion (RRF)
    • BM25 score fusion
    • Learning-to-Rank
    """

    def __init__(
        self,
        config: RetrievalConfig | None = None
    ):

        self.config = config or RetrievalConfig()

    def combine(
        self,
        semantic: dict | None,
        keyword: dict | None,
        k: int
    ) -> dict:

        merged = {}

        if (
            semantic is not None
            and self.config.enable_semantic
        ):
            self._merge(
                merged,
                semantic,
                source="semantic"
            )

        if (
            keyword is not None
            and self.config.enable_keyword
        ):
            self._merge(
                merged,
                keyword,
                source="keyword"
            )

        items = sorted(
            merged.items(),
            key=lambda item: item[1]["score"],
            reverse=True
        )[:k]

        return {
            "ids": [[item[0] for item in items]],
            "documents": [[item[1]["document"] for item in items]],
            "metadatas": [[item[1]["metadata"] for item in items]],
            "distances": [[item[1]["distance"] for item in items]]
        }

    def _merge(
        self,
        merged: dict,
        results: dict,
        source: str
    ):

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        weight = (
            self.config.semantic_weight
            if source == "semantic"
            else self.config.keyword_weight
        )

        for doc_id, document, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances
        ):

            #
            # Chroma distances:
            # smaller distance = better match.
            #
            if source == "semantic":

                score = (
                    1.0 / (1.0 + distance)
                ) * weight

            else:

                #
                # Keyword retriever currently
                # returns 0.0 for all distances.
                #
                score = weight

            if doc_id not in merged:

                merged[doc_id] = {
                    "document": document,
                    "metadata": metadata,
                    "distance": distance,
                    "score": score
                }

            else:

                merged[doc_id]["score"] += score


result_fusion = ResultFusion()