from app.rag.base_retriever import BaseRetriever
from app.rag.bm25_index import bm25_index
from app.rag.vector_store import vector_store


class KeywordRetriever(BaseRetriever):
    """
    BM25-backed keyword retriever.

    This class acts as an adapter between the BM25 index
    and the existing hybrid retrieval pipeline.

    BM25 returns document indices and scores.

    This adapter converts those indices back into the
    ChromaDB-style retrieval format expected by the rest
    of the RAG pipeline.
    """

    def retrieve(
        self,
        query: str,
        k: int = 3,
    ) -> dict:

        corpus = vector_store.get_all_chunks()

        ids = corpus.get(
            "ids",
            [],
        )

        documents = corpus.get(
            "documents",
            [],
        )

        metadatas = corpus.get(
            "metadatas",
            [],
        )

        bm25_results = bm25_index.search(
            query=query,
            k=k,
        )

        selected_ids = []
        selected_documents = []
        selected_metadatas = []
        selected_scores = []

        for document_index, score in bm25_results:

            #
            # Safety check
            #

            if (
                document_index < 0
                or document_index >= len(documents)
            ):
                continue

            selected_ids.append(
                ids[document_index]
            )

            selected_documents.append(
                documents[document_index]
            )

            selected_metadatas.append(
                metadatas[document_index]
            )

            selected_scores.append(
                score
            )

        return {
            "ids": [selected_ids],
            "documents": [selected_documents],
            "metadatas": [selected_metadatas],
            "distances": [selected_scores],
        }


keyword_retriever = KeywordRetriever()