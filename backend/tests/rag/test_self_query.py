from app.rag.intelligence.self_query import (
    SelfQueryResult,
    SelfQueryRetriever,
    self_query_retriever,
)


def test_plain_semantic_query():

    result = self_query_retriever.parse(
        "machine learning fundamentals"
    )

    assert isinstance(
        result,
        SelfQueryResult,
    )

    assert result.query == (
        "machine learning fundamentals"
    )

    assert result.filters == {}


def test_filename_constraint():

    result = self_query_retriever.parse(
        "machine learning filename research.pdf"
    )

    assert result.query == "machine learning"

    assert result.filters == {
        "filename": "research.pdf",
    }


def test_source_constraint():

    result = self_query_retriever.parse(
        "retrieval augmented generation from research.pdf"
    )

    assert result.query == (
        "retrieval augmented generation"
    )

    assert result.filters == {
        "source": "research.pdf",
    }


def test_document_type_constraint():

    result = self_query_retriever.parse(
        "medical imaging document type pdf"
    )

    assert result.query == "medical imaging"

    assert result.filters == {
        "document_type": "pdf",
    }


def test_mime_type_constraint():

    result = self_query_retriever.parse(
        "medical report mime type application/pdf"
    )

    assert result.query == "medical report"

    assert result.filters == {
        "mime_type": "application/pdf",
    }


def test_asset_id_constraint():

    result = self_query_retriever.parse(
        "retrieve this document asset id asset-123"
    )

    assert result.query == (
        "retrieve this document"
    )

    assert result.filters == {
        "asset_id": "asset-123",
    }


def test_multiple_constraints():

    result = self_query_retriever.parse(
        "machine learning "
        "filename research.pdf "
        "document type pdf"
    )

    assert result.query == "machine learning"

    assert result.filters == {
        "filename": "research.pdf",
        "document_type": "pdf",
    }


def test_case_insensitive_filter_extraction():

    result = self_query_retriever.parse(
        "Explain transformers "
        "FILENAME paper.pdf"
    )

    assert result.query == (
        "Explain transformers"
    )

    assert result.filters == {
        "filename": "paper.pdf",
    }


def test_query_without_filters_is_preserved():

    query = (
        "Explain how retrieval augmented "
        "generation works"
    )

    result = self_query_retriever.parse(
        query
    )

    assert result.query == query
    assert result.filters == {}


def test_empty_query_returns_empty_result():

    result = self_query_retriever.parse(
        "   "
    )

    assert result.query == ""
    assert result.filters == {}


def test_unknown_metadata_is_not_extracted():

    result = self_query_retriever.parse(
        "machine learning collection research"
    )

    assert result.query == (
        "machine learning collection research"
    )

    assert result.filters == {}


def test_original_query_is_not_mutated():

    query = (
        "machine learning filename research.pdf"
    )

    result = self_query_retriever.parse(
        query
    )

    assert query == (
        "machine learning filename research.pdf"
    )

    assert result.query == "machine learning"


def test_parser_is_deterministic():

    query = (
        "retrieval filename paper.pdf "
        "document type pdf"
    )

    first = self_query_retriever.parse(
        query
    )

    second = self_query_retriever.parse(
        query
    )

    assert first == second


def test_source_alias_is_supported():

    result = self_query_retriever.parse(
        "retrieval source=research.pdf"
    )

    assert result.query == "retrieval"

    assert result.filters == {
        "source": "research.pdf",
    }


def test_filename_alias_is_supported():

    result = self_query_retriever.parse(
        "python filename=guide.pdf"
    )

    assert result.query == "python"

    assert result.filters == {
        "filename": "guide.pdf",
    }


def test_asset_alias_is_supported():

    result = self_query_retriever.parse(
        "python asset=asset-456"
    )

    assert result.query == "python"

    assert result.filters == {
        "asset_id": "asset-456",
    }


def test_whitespace_is_normalized():

    result = self_query_retriever.parse(
        "  machine    learning   filename   paper.pdf  "
    )

    assert result.query == "machine learning"

    assert result.filters == {
        "filename": "paper.pdf",
    }