from app.rag.rag_service import rag_service


def test_rag_diagnostics_initial_state():
    diagnostics = rag_service.diagnostics()
    assert isinstance(diagnostics, dict)
    assert "message" in diagnostics or "request" in diagnostics