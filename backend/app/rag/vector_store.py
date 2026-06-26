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
        metadata: dict | None = None
    ):

        embedding = embedding_service.embed(text)

        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata or {}]
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


vector_store = VectorStore()