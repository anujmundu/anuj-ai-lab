import re

from app.rag.base_retriever import BaseRetriever
from app.rag.vector_store import vector_store


class KeywordRetriever(BaseRetriever):
    """
    Lightweight keyword retriever.

    Uses a lightweight lexical similarity score based on:

    • Overlap Coefficient
    • Query Term Density

    This keeps the implementation simple while producing
    better rankings than raw token overlap.

    Future implementations may replace this with:

    • BM25
    • SQLite FTS5
    • Elasticsearch
    • OpenSearch
    • Whoosh
    """

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

    def _keyword_score(
        self,
        query_tokens: set[str],
        document_tokens: set[str]
    ) -> float:

        if not query_tokens or not document_tokens:
            return 0.0

        overlap = query_tokens.intersection(
            document_tokens
        )

        if not overlap:
            return 0.0

        overlap_coefficient = (
            len(overlap)
            / min(
                len(query_tokens),
                len(document_tokens)
            )
        )

        query_term_density = (
            len(overlap)
            / len(document_tokens)
        )

        return (
            0.7 * overlap_coefficient
            +
            0.3 * query_term_density
        )

    def retrieve(
        self,
        query: str,
        k: int = 3
    ):

        query_tokens = self._tokenize(query)

        results = vector_store.collection.get()

        ids = results.get("ids", [])
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])

        scored = []

        for doc_id, document, metadata in zip(
            ids,
            documents,
            metadatas
        ):

            document_tokens = self._tokenize(
                document
            )

            score = self._keyword_score(
                query_tokens,
                document_tokens
            )

            if score > 0:

                scored.append(
                    (
                        score,
                        doc_id,
                        document,
                        metadata
                    )
                )

        scored.sort(
            key=lambda item: item[0],
            reverse=True
        )

        scored = scored[:k]

        return {
            "ids": [[item[1] for item in scored]],
            "documents": [[item[2] for item in scored]],
            "metadatas": [[item[3] for item in scored]],
            "distances": [[item[0] for item in scored]]
        }


keyword_retriever = KeywordRetriever()