from app.rag.parent_child import ParentChunk
from app.rag.parent_context import ParentContextRegistry
from app.rag.parent_context_resolver import (
    ParentContextResolver,
)
from app.rag.retrieval_models import (
    RetrievalMetadata,
    RetrievalResult,
    RetrievalScores,
)


def make_parent(
    parent_id: str,
    index: int,
) -> ParentChunk:
    return ParentChunk(
        parent_id=parent_id,
        text=f"Parent context {index}",
        index=index,
    )


def make_result(
    *,
    doc_id: str,
    child_id: str,
    parent_id: str = "",
) -> RetrievalResult:
    return RetrievalResult(
        doc_id=doc_id,
        document=f"Document content for {child_id}",
        metadata=RetrievalMetadata(
            filename="document.txt",
            chunk_id=child_id,
            parent_id=parent_id,
            child_id=child_id,
            chunk_number=0,
            total_chunks=3,
            source="test",
        ),
        scores=RetrievalScores(
            semantic_score=0.9,
            keyword_score=0.8,
            combined_score=0.85,
        ),
    )


def make_registry() -> ParentContextRegistry:
    return ParentContextRegistry(
        (
            make_parent(
                "document-1:parent:0",
                0,
            ),
            make_parent(
                "document-1:parent:1",
                1,
            ),
            make_parent(
                "document-1:parent:2",
                2,
            ),
        )
    )


def test_child_parent_id_resolves_parent():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    results = [
        make_result(
            doc_id="child-0",
            child_id="document-1:child:0",
            parent_id="document-1:parent:0",
        )
    ]

    resolved = resolver.resolve(results)

    assert len(resolved) == 1
    assert (
        resolved[0].parent.parent_id
        == "document-1:parent:0"
    )


def test_multiple_children_same_parent_produce_one_parent():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    results = [
        make_result(
            doc_id="child-0",
            child_id="document-1:child:0",
            parent_id="document-1:parent:0",
        ),
        make_result(
            doc_id="child-1",
            child_id="document-1:child:1",
            parent_id="document-1:parent:0",
        ),
    ]

    resolved = resolver.resolve(results)

    assert len(resolved) == 1

    assert resolved[0].child_ids == (
        "document-1:child:0",
        "document-1:child:1",
    )


def test_parent_order_follows_first_retrieval_occurrence():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    results = [
        make_result(
            doc_id="child-2",
            child_id="document-1:child:2",
            parent_id="document-1:parent:2",
        ),
        make_result(
            doc_id="child-0",
            child_id="document-1:child:0",
            parent_id="document-1:parent:0",
        ),
        make_result(
            doc_id="child-1",
            child_id="document-1:child:1",
            parent_id="document-1:parent:1",
        ),
    ]

    resolved = resolver.resolve(results)

    assert [
        item.parent.parent_id
        for item in resolved
    ] == [
        "document-1:parent:2",
        "document-1:parent:0",
        "document-1:parent:1",
    ]


def test_repeated_parent_ids_are_deduplicated():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    results = [
        make_result(
            doc_id="child-0",
            child_id="document-1:child:0",
            parent_id="document-1:parent:0",
        ),
        make_result(
            doc_id="child-1",
            child_id="document-1:child:1",
            parent_id="document-1:parent:0",
        ),
        make_result(
            doc_id="child-2",
            child_id="document-1:child:2",
            parent_id="document-1:parent:0",
        ),
    ]

    resolved = resolver.resolve(results)

    assert len(resolved) == 1


def test_child_without_parent_id_remains_valid():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    results = [
        make_result(
            doc_id="child-standalone",
            child_id="child-standalone",
        )
    ]

    resolved = resolver.resolve(results)

    assert resolved == ()


def test_unknown_parent_id_is_ignored():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    results = [
        make_result(
            doc_id="child-unknown",
            child_id="child-unknown",
            parent_id="document-1:parent:unknown",
        )
    ]

    resolved = resolver.resolve(results)

    assert resolved == ()


def test_unknown_parent_does_not_hide_known_parent():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    results = [
        make_result(
            doc_id="unknown",
            child_id="unknown",
            parent_id="missing-parent",
        ),
        make_result(
            doc_id="known",
            child_id="document-1:child:1",
            parent_id="document-1:parent:1",
        ),
    ]

    resolved = resolver.resolve(results)

    assert len(resolved) == 1

    assert (
        resolved[0].parent.parent_id
        == "document-1:parent:1"
    )


def test_original_retrieval_results_are_not_modified():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    result = make_result(
        doc_id="child-0",
        child_id="document-1:child:0",
        parent_id="document-1:parent:0",
    )

    original_metadata = result.metadata

    resolver.resolve([result])

    assert result.metadata is original_metadata

    assert result.parent_id == (
        "document-1:parent:0"
    )

    assert result.child_id == (
        "document-1:child:0"
    )


def test_child_ids_are_grouped_deterministically():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    results = [
        make_result(
            doc_id="child-2",
            child_id="document-1:child:2",
            parent_id="document-1:parent:1",
        ),
        make_result(
            doc_id="child-1",
            child_id="document-1:child:1",
            parent_id="document-1:parent:1",
        ),
        make_result(
            doc_id="child-3",
            child_id="document-1:child:3",
            parent_id="document-1:parent:1",
        ),
    ]

    resolved = resolver.resolve(results)

    assert resolved[0].child_ids == (
        "document-1:child:2",
        "document-1:child:1",
        "document-1:child:3",
    )


def test_empty_results_return_empty_tuple():
    registry = make_registry()
    resolver = ParentContextResolver(registry)

    assert resolver.resolve([]) == ()