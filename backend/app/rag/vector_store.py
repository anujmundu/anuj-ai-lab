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

    def add_document(
        self,
        doc_id: str,
        text: str
    ):

        embedding = embedding_service.embed(text)

        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding]
        )

    def search(
        self,
        query: str,
        k: int = 3
    ):

        embedding = embedding_service.embed(query)

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=k
        )

        return results


vector_store = VectorStore()