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

    def add(
        self,
        doc_id: str,
        text: str,
        metadata: dict
    ):

        embedding = embedding_service.embed(text)

        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata]
        )

    def search(
        self,
        query: str,
        k: int = 3
    ):

        embedding = embedding_service.embed(query)

        return self.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )

    def get_document_chunks(
        self,
        filename: str
    ):

        return self.collection.get(
            where={
                "filename": filename
            }
        )

    def delete_document(
        self,
        filename: str
    ):

        chunks = self.get_document_chunks(
            filename
        )

        ids = chunks["ids"]

        if ids:
            self.collection.delete(
                ids=ids
            )

    def get_documents(self):

        results = self.collection.get()

        metadatas = results.get("metadatas") or []

        documents = {}

        for metadata in metadatas:

            if metadata is None:
                continue

            filename = metadata["filename"]

            documents[filename] = documents.get(
                filename,
                0
            ) + 1

        return documents

    def document_exists(
        self,
        filename: str
    ) -> bool:

        chunks = self.get_document_chunks(
            filename
        )

        return len(chunks["ids"]) > 0


vector_store = VectorStore()