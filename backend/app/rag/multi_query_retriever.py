from __future__ import annotations

from app.rag.base_retriever import BaseRetriever
from app.rag.hybrid_retriever import hybrid_retriever
from app.rag.query.models import QueryAnalysisResult
from app.rag.query.query_generator import query_generator


class MultiQueryRetriever(BaseRetriever):
    """
    Executes multiple retrieval queries and merges their results.

    Each individual query is delegated to the existing
    HybridRetriever.

    The final result follows the standard retrieval result
    contract used throughout the RAG pipeline.
    """

    def retrieve(
        self,
        *,
        query: str,
        k: int,
        analysis: QueryAnalysisResult,
        profiler=None,
    ) -> dict:

        queries = query_generator.generate(
            query=query,
            analysis=analysis,
        )

        if not queries:
            return self._empty_result()

        query_results = []

        for generated_query in queries:

            result = hybrid_retriever.retrieve(
                query=generated_query,
                k=k,
                profiler=profiler,
            )

            query_results.append(
                (
                    generated_query,
                    result,
                )
            )

        merged = {}

        for generated_query, result in query_results:

            ids = result.get(
                "ids",
                [[]],
            )[0]

            documents = result.get(
                "documents",
                [[]],
            )[0]

            metadatas = result.get(
                "metadatas",
                [[]],
            )[0]

            distances = result.get(
                "distances",
                [[]],
            )[0]

            embeddings = result.get(
                "embeddings",
                [[]],
            )[0]

            retrieval = result.get(
                "retrieval",
                [[]],
            )[0]

            for index, doc_id in enumerate(ids):

                document = documents[index]
                metadata = metadatas[index]
                distance = distances[index]
                embedding = (
                    embeddings[index]
                    if index < len(embeddings)
                    else None
                )

                scores = (
                    retrieval[index]
                    if index < len(retrieval)
                    else {}
                )

                combined_score = scores.get(
                    "combined_score",
                    0.0,
                )

                if doc_id not in merged:

                    merged[doc_id] = {
                        "document": document,
                        "metadata": metadata,
                        "distance": distance,
                        "embedding": embedding,
                        "semantic_score": scores.get(
                            "semantic_score",
                            0.0,
                        ),
                        "keyword_score": scores.get(
                            "keyword_score",
                            0.0,
                        ),
                        "combined_score": combined_score,
                        "query_hits": 1,
                        "queries": [
                            generated_query,
                        ],
                    }

                else:

                    item = merged[doc_id]

                    item["semantic_score"] = max(
                        item["semantic_score"],
                        scores.get(
                            "semantic_score",
                            0.0,
                        ),
                    )

                    item["keyword_score"] = max(
                        item["keyword_score"],
                        scores.get(
                            "keyword_score",
                            0.0,
                        ),
                    )

                    item["combined_score"] += (
                        combined_score
                    )

                    item["query_hits"] += 1

                    item["queries"].append(
                        generated_query
                    )

        ranked = sorted(
            merged.items(),
            key=lambda item: (
                item[1]["combined_score"],
                item[1]["query_hits"],
            ),
            reverse=True,
        )[:k]

        return {
            "ids": [[
                doc_id
                for doc_id, _ in ranked
            ]],
            "documents": [[
                item["document"]
                for _, item in ranked
            ]],
            "metadatas": [[
                item["metadata"]
                for _, item in ranked
            ]],
            "distances": [[
                item["distance"]
                for _, item in ranked
            ]],
            "embeddings": [[
                item["embedding"]
                for _, item in ranked
            ]],
            "retrieval": [[
                {
                    "semantic_score": item[
                        "semantic_score"
                    ],
                    "keyword_score": item[
                        "keyword_score"
                    ],
                    "combined_score": item[
                        "combined_score"
                    ],
                    "semantic_rank": None,
                    "keyword_rank": None,
                    "query_hits": item[
                        "query_hits"
                    ],
                }
                for _, item in ranked
            ]],
            "pipeline": {
                "strategy": "multi_query",
                "generated_queries": queries,
                "query_count": len(queries),
                "unique_documents": len(merged),
            },
        }

    @staticmethod
    def _empty_result() -> dict:

        return {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
            "embeddings": [[]],
            "retrieval": [[]],
            "pipeline": {
                "strategy": "multi_query",
                "generated_queries": [],
                "query_count": 0,
                "unique_documents": 0,
            },
        }


multi_query_retriever = MultiQueryRetriever()
