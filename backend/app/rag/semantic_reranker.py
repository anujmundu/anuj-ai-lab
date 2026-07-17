from copy import deepcopy
from dataclasses import dataclass

from app.rag.semantic_matcher import semantic_matcher
from app.rag.semantic_reranker_config import SemanticRerankerConfig


@dataclass(slots=True)
class RerankCandidate:
    """
    Represents a semantic retrieval candidate after
    score fusion but before final ranking.
    """

    index: int
    semantic_similarity: float
    chroma_similarity: float
    rerank_score: float
    
class SemanticReranker:

    """
    Re-ranks semantic retrieval candidates using both
    the original Chroma similarity and SemanticMatcher.

    Pipeline

        ChromaDB Top-K
              │
              ▼
        SemanticMatcher.compare()
              │
              ▼
        Hybrid Score Fusion
              │
              ▼
        Re-ranked Results
    """

    def __init__(
        self,
        config: SemanticRerankerConfig | None = None,
    ):

        self.config = config or SemanticRerankerConfig()

    def rerank(
        self,
        query: str,
        results: dict,
    ) -> dict:
        
        if not self.config.enable_reranking:
            return results
        
        new_results = deepcopy(results)

        ids = new_results.get("ids", [[]])[0]
        documents = new_results.get("documents", [[]])[0]
        metadatas = new_results.get("metadatas", [[]])[0]
        distances = new_results.get("distances", [[]])[0]

        candidates = []

        for index, (
            _,
            document,
            _,
            distance,
        ) in enumerate(
            zip(
                ids,
                documents,
                metadatas,
                distances,
            )
        ):

            comparison = semantic_matcher.compare(
                query,
                document,
            )

            semantic_similarity = (
                comparison["metrics"]["overall"]
            )

            chroma_similarity = (
                1.0
                /
                (
                    1.0
                    + distance
                )
            )

            rerank_score = (
                self.config.chroma_weight
                * chroma_similarity
                +
                self.config.semantic_weight
                * semantic_similarity
            )

            candidates.append(
                RerankCandidate(
                    index=index,
                    semantic_similarity=semantic_similarity,
                    chroma_similarity=chroma_similarity,
                    rerank_score=rerank_score,
                )
            )

        candidates.sort(
            key=lambda item: item.rerank_score,
            reverse=True,
        )

        order = [
            candidate.index
            for candidate in candidates
        ]

        new_results["ids"][0] = [
            ids[i]
            for i in order
        ]

        new_results["documents"][0] = [
            documents[i]
            for i in order
        ]

        new_results["metadatas"][0] = [
            metadatas[i]
            for i in order
        ]

        new_results["distances"][0] = [
            distances[i]
            for i in order
        ]
        
        new_results["semantic_similarity"] = [[
            candidate.semantic_similarity
            for candidate in candidates
        ]]

        new_results["chroma_similarity"] = [[
            candidate.chroma_similarity
            for candidate in candidates
        ]]

        new_results["rerank_scores"] = [[
            candidate.rerank_score
            for candidate in candidates
        ]]

        if self.config.include_diagnostics:

            new_results["reranking"] = [[
                {
                    "chroma_similarity": round(
                        candidate.chroma_similarity,
                        3,
                    ),
                    "semantic_similarity": round(
                        candidate.semantic_similarity,
                        3,
                    ),
                    "rerank_score": round(
                        candidate.rerank_score,
                        3,
                    ),
                }
                for candidate in candidates
            ]]

        requested_k = new_results.get(
            "requested_k",
            len(new_results["ids"][0]),
        )

        for key in (
            "ids",
            "documents",
            "metadatas",
            "distances",
            "semantic_similarity",
            "chroma_similarity",
            "rerank_scores",
        ):

            if key in new_results:

                new_results[key][0] = new_results[key][0][:requested_k]

        if (
            self.config.include_diagnostics
            and
            "reranking" in new_results
        ):

            new_results["reranking"][0] = (
                new_results["reranking"][0][:requested_k]
            )

        return new_results


semantic_reranker = SemanticReranker()