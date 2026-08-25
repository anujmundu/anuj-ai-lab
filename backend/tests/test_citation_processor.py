from app.rag.citation_processor import citation_processor
from app.rag.evidence_models import EvidenceAlignmentResult


def test_citation_processor_process():
    answer = (
        "ChromaDB is an open-source vector database [1] "
        "designed for AI applications."
    )
    sources = [
        {
            "filename": "python_notes",
            "chunk_id": "python_notes_chunk_004",
            "chunk_number": 4,
            "total_chunks": 9,
        },
    ]

    result = citation_processor.process(
        answer=answer,
        sources=sources,
        alignment=EvidenceAlignmentResult(),
    )

    assert "answer" in result
    assert "citations" in result
    assert "source_mapping" in result
