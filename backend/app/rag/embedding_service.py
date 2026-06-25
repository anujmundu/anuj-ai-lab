from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):

        print("Loading embedding model...")

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded.")

    def embed(
        self,
        text: str
    ):

        return self.model.encode(
            text
        ).tolist()


embedding_service = EmbeddingService()