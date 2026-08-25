from app.rag.chunk_config import ChunkingConfig
from app.rag.chunk_strategy import ChunkStrategy
from app.rag.text_chunker import text_chunker


def test_sentence_chunking_and_overlap():
    long_paragraph = (
        "Python is a programming language. Python was created by Guido. "
        "FastAPI is a modern API framework. ChromaDB stores vector embeddings. "
        "Sentence Transformers generate embeddings. RAG improves LLM accuracy."
    )
    chunks = text_chunker.chunk(
        text=long_paragraph,
        config=ChunkingConfig(
            chunk_size=120,
            overlap_sentences=1,
            strategy=ChunkStrategy.SENTENCE,
        ),
    )
    assert len(chunks) > 1
    assert all(len(c) > 0 for c in chunks)


def test_paragraph_chunking():
    doc = "Paragraph 1 is here.\n\nParagraph 2 is here.\n\nParagraph 3 is here."
    chunks = text_chunker.chunk(
        text=doc,
        config=ChunkingConfig(
            chunk_size=25,
            strategy=ChunkStrategy.PARAGRAPH,
        ),
    )
    assert len(chunks) == 3
    assert "Paragraph 1 is here." in chunks[0]



def test_markdown_chunking():
    doc = "# Introduction\nOverview of RAG.\n\n## Architecture\nDetails about ChromaDB and BM25.\n\n## Evaluation\nRegression gates."
    chunks = text_chunker.chunk(
        text=doc,
        config=ChunkingConfig(
            chunk_size=100,
            strategy=ChunkStrategy.MARKDOWN,
        ),
    )
    assert len(chunks) == 3
    assert "# Introduction" in chunks[0]
    assert "## Architecture" in chunks[1]
    assert "## Evaluation" in chunks[2]


def test_code_chunking():
    code = (
        "def func_one():\n    return 1\n\n"
        "def func_two():\n    return 2\n\n"
        "class Service:\n    pass\n"
    )
    chunks = text_chunker.chunk(
        text=code,
        config=ChunkingConfig(
            chunk_size=50,
            strategy=ChunkStrategy.CODE,
        ),
    )
    assert len(chunks) >= 3
    assert "def func_one():" in chunks[0]


def test_fixed_chunking():
    text = "A" * 200
    chunks = text_chunker.chunk(
        text=text,
        config=ChunkingConfig(
            chunk_size=50,
            strategy=ChunkStrategy.FIXED,
        ),
    )
    assert len(chunks) >= 4