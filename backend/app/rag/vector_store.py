import chromadb

from app.rag.bm25_index import bm25_index
from app.rag.embedding_service import embedding_service


class VectorStore:
    """
    Persistent vector database backed by ChromaDB.

    Responsibilities

    • Store embeddings
    • Semantic retrieval
    • Document CRUD
    • BM25 synchronization
    """

    def __init__(self):

        print("Initializing ChromaDB...")

        self.client = chromadb.PersistentClient(
            path="vector_db",
        )

        self.collection = (
            self.client.get_or_create_collection(
                name="documents",
            )
        )

        print("ChromaDB ready.")

    # --------------------------------------------------
    # CRUD
    # --------------------------------------------------

    def add(
        self,
        doc_id: str,
        text: str,
        metadata: dict,
    ) -> None:

        embedding = embedding_service.embed(
            text,
        )

        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
        )

    def search(
        self,
        query: str,
        k: int = 3,
    ):

        embedding = embedding_service.embed(
            query,
        )

        return self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
        )

    # --------------------------------------------------
    # Retrieval
    # --------------------------------------------------

    def get_document_chunks(
        self,
        filename: str,
    ):

        return self.collection.get(
            where={
                "filename": filename,
            }
        )

    def get_all_chunks(
        self,
    ) -> dict:
        """
        Return the complete corpus.

        Used by:

        • BM25
        • Diagnostics
        • Corpus statistics
        • Evaluation
        """

        return self.collection.get()

    # --------------------------------------------------
    # BM25 Synchronization
    # --------------------------------------------------

    def sync_bm25_index(
        self,
    ) -> dict:
        """
        Synchronize the in-memory BM25 index
        with the current ChromaDB corpus.
        """

        corpus = self.get_all_chunks()

        documents = (
            corpus.get("documents")
            or []
        )

        bm25_index.rebuild(
            documents,
        )

        stats = {
            "documents_loaded": len(documents),
            "bm25_documents": bm25_index.document_count,
        }

        print(
            f"BM25 synchronized ({stats['bm25_documents']} documents)."
        )

        return stats

    # --------------------------------------------------
    # Deletion
    # --------------------------------------------------

    def delete_document(
        self,
        filename: str,
        sync_bm25: bool = True,
    ) -> None:

        chunks = self.get_document_chunks(
            filename,
        )

        ids = chunks["ids"]

        if ids:

            self.collection.delete(
                ids=ids,
            )

            if sync_bm25:
                self.sync_bm25_index()

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    def get_documents(
        self,
    ) -> dict:

        results = self.get_all_chunks()

        metadatas = (
            results.get("metadatas")
            or []
        )

        documents = {}

        for metadata in metadatas:

            if metadata is None:
                continue

            filename = metadata["filename"]

            documents[filename] = (
                documents.get(
                    filename,
                    0,
                )
                + 1
            )

        return documents

    def document_exists(
        self,
        filename: str,
    ) -> bool:

        chunks = self.get_document_chunks(
            filename,
        )

        return (
            len(chunks["ids"]) > 0
        )


vector_store = VectorStore()