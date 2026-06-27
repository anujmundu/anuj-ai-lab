import re

from app.rag.base_retriever import BaseRetriever
from app.rag.vector_store import vector_store


class KeywordRetriever(BaseRetriever):
    """
    Lightweight keyword retriever.

    Uses simple token-overlap scoring.

    Future implementations can replace this with:

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

            overlap = query_tokens.intersection(
                document_tokens
            )

            score = len(overlap)

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
            "distances": [[0.0] * len(scored)]
        }


keyword_retriever = KeywordRetriever()