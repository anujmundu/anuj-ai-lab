from app.rag.parent_child import ParentChildBuilder
from app.rag.parent_child_metadata import (
    ParentChildMetadataBuilder,
)


def make_children() -> list[str]:
    return [
        "Child one content.",
        "Child two content.",
        "Child three content.",
        "Child four content.",
    ]


def build_document():
    builder = ParentChildBuilder(
        children_per_parent=2,
    )

    return builder.build(
        make_children(),
        document_id="document-1",
    )


def test_child_metadata_preserves_existing_chunk_fields():
    document = build_document()

    child = document.children[0]

    metadata_builder = ParentChildMetadataBuilder()

    metadata = metadata_builder.build_child_metadata(
        filename="document.txt",
        chunk_number=1,
        total_chunks=len(document.children),
        child=child,
    )

    assert metadata["filename"] == "document.txt"

    assert metadata["chunk_number"] == 1
    assert metadata["total_chunks"] == 4

    assert metadata["chunk_id"] == child.child_id

    assert metadata["child_id"] == child.child_id
    assert metadata["parent_id"] == child.parent_id

    assert metadata["chunk_type"] == "child"


def test_child_metadata_relationship_is_deterministic():
    document = build_document()

    first_child = document.children[0]
    second_child = document.children[1]

    metadata_builder = ParentChildMetadataBuilder()

    first = metadata_builder.build_child_metadata(
        filename="document.txt",
        chunk_number=1,
        total_chunks=len(document.children),
        child=first_child,
    )

    second = metadata_builder.build_child_metadata(
        filename="document.txt",
        chunk_number=2,
        total_chunks=len(document.children),
        child=second_child,
    )

    assert first["parent_id"] == second["parent_id"]

    assert first["child_id"] != second["child_id"]

    assert first["child_id"] == first["chunk_id"]
    assert second["child_id"] == second["chunk_id"]


def test_parent_metadata_contains_parent_identity():
    document = build_document()

    parent = document.parents[0]

    metadata_builder = ParentChildMetadataBuilder()

    metadata = metadata_builder.build_parent_metadata(
        filename="document.txt",
        parent=parent,
    )

    assert metadata["filename"] == "document.txt"

    assert metadata["parent_id"] == parent.parent_id

    assert metadata["chunk_type"] == "parent"

    assert metadata["parent_index"] == parent.index

def test_child_metadata_does_not_require_parent_indexing():
    document = build_document()

    metadata_builder = ParentChildMetadataBuilder()

    child_metadata = [
        metadata_builder.build_child_metadata(
            filename="document.txt",
            chunk_number=index,
            total_chunks=len(document.children),
            child=child,
        )
        for index, child in enumerate(
            document.children,
            start=1,
        )
    ]

    assert len(child_metadata) == 4

    assert all(
        metadata["chunk_type"] == "child"
        for metadata in child_metadata
    )

    assert all(
        metadata["parent_id"]
        for metadata in child_metadata
    )

    assert all(
        metadata["child_id"]
        for metadata in child_metadata
    )

    assert all(
        metadata["child_id"] == metadata["chunk_id"]
        for metadata in child_metadata
    )