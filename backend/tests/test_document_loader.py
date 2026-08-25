from app.rag.document_loader import document_loader


def test_load_txt(tmp_path):
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text(
        "Hello, RAG!",
        encoding="utf-8",
    )

    text = document_loader.load(str(sample_file))
    assert text == "Hello, RAG!"


def test_load_markdown(tmp_path):
    md_file = tmp_path / "docs.md"
    md_file.write_text(
        "# Heading\n\nSome documentation text.",
        encoding="utf-8",
    )
    text = document_loader.load(str(md_file))
    assert "# Heading" in text


def test_load_json(tmp_path):
    json_file = tmp_path / "data.json"
    json_file.write_text(
        '{"name": "Anuj AI Lab", "version": "1.2.0"}',
        encoding="utf-8",
    )
    text = document_loader.load(str(json_file))
    assert "Anuj AI Lab" in text


def test_load_csv_as_markdown_table(tmp_path):
    csv_file = tmp_path / "metrics.csv"
    csv_file.write_text(
        "metric,score\naccuracy,0.95\nlatency,12ms",
        encoding="utf-8",
    )
    text = document_loader.load(str(csv_file))
    assert "accuracy" in text
    assert "0.95" in text


def test_load_python_code(tmp_path):
    py_file = tmp_path / "script.py"
    py_file.write_text(
        "def hello_world():\n    return 'hello'\n",
        encoding="utf-8",
    )
    text = document_loader.load(str(py_file))
    assert "def hello_world():" in text