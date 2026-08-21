from app.rag.parent_child import (
    ChildChunk,
    ParentChunk,
    ParentChildBuilder,
)


def test_builder_groups_children_into_parents():

    builder = ParentChildBuilder(
        children_per_parent=2,
    )

    result = builder.build(
        [
            "chunk one",
            "chunk two",
            "chunk three",
            "chunk four",
            "chunk five",
        ],
        document_id="doc-1",
    )

    assert len(result.parents) == 3
    assert len(result.children) == 5


def test_parent_ids_are_deterministic():

    builder = ParentChildBuilder(
        children_per_parent=2,
    )

    result = builder.build(
        [
            "chunk one",
            "chunk two",
            "chunk three",
        ],
        document_id="doc-1",
    )

    assert result.parents[0].parent_id == (
        "doc-1:parent:0"
    )

    assert result.parents[1].parent_id == (
        "doc-1:parent:1"
    )


def test_child_ids_are_deterministic():

    builder = ParentChildBuilder(
        children_per_parent=2,
    )

    result = builder.build(
        [
            "chunk one",
            "chunk two",
            "chunk three",
        ],
        document_id="doc-1",
    )

    assert result.children[0].child_id == (
        "doc-1:child:0"
    )

    assert result.children[1].child_id == (
        "doc-1:child:1"
    )

    assert result.children[2].child_id == (
        "doc-1:child:2"
    )


def test_children_reference_their_parent():

    builder = ParentChildBuilder(
        children_per_parent=2,
    )

    result = builder.build(
        [
            "chunk one",
            "chunk two",
            "chunk three",
        ],
        document_id="doc-1",
    )

    assert result.children[0].parent_id == (
        result.parents[0].parent_id
    )

    assert result.children[1].parent_id == (
        result.parents[0].parent_id
    )

    assert result.children[2].parent_id == (
        result.parents[1].parent_id
    )


def test_parent_contains_child_context():

    builder = ParentChildBuilder(
        children_per_parent=2,
    )

    result = builder.build(
        [
            "chunk one",
            "chunk two",
            "chunk three",
        ],
        document_id="doc-1",
    )

    assert result.parents[0].text == (
        "chunk one chunk two"
    )

    assert result.parents[1].text == (
        "chunk three"
    )


def test_child_text_is_preserved():

    chunks = [
        "chunk one",
        "chunk two",
        "chunk three",
    ]

    builder = ParentChildBuilder(
        children_per_parent=2,
    )

    result = builder.build(
        chunks,
        document_id="doc-1",
    )

    assert [
        child.text
        for child in result.children
    ] == chunks


def test_empty_chunks_produce_empty_document():

    builder = ParentChildBuilder()

    result = builder.build(
        [],
        document_id="doc-1",
    )

    assert result.parents == ()
    assert result.children == ()


def test_invalid_children_per_parent_is_rejected():

    try:
        ParentChildBuilder(
            children_per_parent=0,
        )
    except ValueError as exc:
        assert str(exc) == (
            "children_per_parent must be at least 1"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_empty_document_id_is_rejected():

    builder = ParentChildBuilder()

    try:
        builder.build(
            ["chunk"],
            document_id="   ",
        )
    except ValueError as exc:
        assert str(exc) == (
            "document_id must not be empty"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_parent_and_child_are_immutable():

    parent = ParentChunk(
        parent_id="parent-1",
        text="parent",
        index=0,
    )

    child = ChildChunk(
        child_id="child-1",
        parent_id="parent-1",
        text="child",
        index=0,
    )

    try:
        parent.text = "changed"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "ParentChunk should be immutable"
        )

    try:
        child.text = "changed"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "ChildChunk should be immutable"
        )