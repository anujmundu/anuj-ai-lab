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

        chunks = self.get_document_chunks(filename)

        ids = chunks["ids"]

        if ids:
            self.collection.delete(
                ids=ids
            )


vector_store = VectorStore()