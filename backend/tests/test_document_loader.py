from app.rag.document_loader import document_loader


def test_load_txt(tmp_path):
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text(
        "Hello, RAG!",
        encoding="utf-8",
    )

    text = document_loader.load(str(sample_file))

    assert text == "Hello, RAG!"