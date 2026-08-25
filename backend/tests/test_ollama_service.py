from unittest.mock import patch, MagicMock

from app.services.ollama_service import OllamaService
from app.services.llm_config import LLMConfig


@patch("requests.post")
def test_ollama_service_generate(mock_post):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": "Mocked LLM answer"}
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    service = OllamaService(LLMConfig(model="qwen2.5:1.5b"))
    result = service.generate(prompt="What is ChromaDB?")

    assert result == "Mocked LLM answer"
    assert service.last_generation["model"] == "qwen2.5:1.5b"