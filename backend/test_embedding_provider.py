from app.rag.ollama_embedding_provider import OllamaEmbeddingProvider
from app.rag.semantic_matcher_config import SemanticMatcherConfig

config = SemanticMatcherConfig()

provider = OllamaEmbeddingProvider(config)

print(provider.diagnostics())

score = provider.similarity(
    "Retrieval-Augmented Generation",
    "RAG retrieves relevant documents before generation",
)

print(f"Similarity: {score:.4f}")