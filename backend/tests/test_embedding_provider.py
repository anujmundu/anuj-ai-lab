from unittest.mock import patch, MagicMock

from app.rag.ollama_embedding_provider import OllamaEmbeddingProvider
from app.rag.semantic_matcher_config import SemanticMatcherConfig


def test_ollama_embedding_provider_diagnostics():
    config = SemanticMatcherConfig()
    provider = OllamaEmbeddingProvider(config)
    diagnostics = provider.diagnostics()
    assert diagnostics["provider"] == "ollama"
    assert "model" in diagnostics


@patch("requests.post")
def test_ollama_embedding_provider_similarity(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"embedding": [0.1, 0.2, 0.3, 0.4]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    config = SemanticMatcherConfig()
    provider = OllamaEmbeddingProvider(config)

    score = provider.similarity(
        "Retrieval-Augmented Generation",
        "RAG retrieves relevant documents before generation",
    )
    assert isinstance(score, float)