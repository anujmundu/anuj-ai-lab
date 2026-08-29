from app.rag.evaluation.synthetic_eval_generator import SyntheticEvalGenerator


def test_synthetic_eval_generation_from_chunk():
    generator = SyntheticEvalGenerator()
    chunk = (
        "FastAPI is a modern web framework for building APIs with Python 3.8+.\n"
        "ChromaDB provides persistent embedding vector indexing for document search."
    )
    items = generator.generate_from_chunk(chunk)

    assert len(items) >= 1
    assert any("FastAPI" in i.question or "ChromaDB" in i.question for i in items)
    assert all(i.ground_truth_context == chunk for i in items)


def test_synthetic_eval_dataset_generation():
    generator = SyntheticEvalGenerator()
    chunks = [
        "Sentence-transformers provides dense vector embeddings.",
        "BM25 provides lexical inverted index keyword retrieval.",
    ]
    dataset = generator.generate_dataset(chunks)
    assert len(dataset) >= 2
