import chromadb

from app.rag.embedding_service import embedding_service


class VectorStore:

    def __init__(self):

        print("Initializing ChromaDB...")

        self.client = chromadb.PersistentClient(
            path="vector_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
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
    ):

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
        Return the complete indexed corpus.

        This serves as the canonical source for
        downstream systems such as:

        • BM25 indexing
        • Corpus statistics
        • Diagnostics
        • Export utilities
        • Offline evaluation
        """

        return self.collection.get()

    # --------------------------------------------------
    # Deletion
    # --------------------------------------------------

    def delete_document(
        self,
        filename: str,
    ):

        chunks = self.get_document_chunks(
            filename,
        )

        ids = chunks["ids"]

        if ids:

            self.collection.delete(
                ids=ids,
            )

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    def get_documents(
        self,
    ):

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

        return len(
            chunks["ids"]
        ) > 0


vector_store = VectorStore()