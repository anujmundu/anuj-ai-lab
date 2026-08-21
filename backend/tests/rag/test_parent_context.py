from app.rag.parent_child import ParentChunk
from app.rag.parent_context import ParentContextRegistry


def make_parent(
    parent_id: str,
    index: int,
    text: str | None = None,
) -> ParentChunk:

    return ParentChunk(
        parent_id=parent_id,
        text=text or f"Parent {index}",
        index=index,
    )


def test_register_and_get_parent():
    registry = ParentContextRegistry()

    parent = make_parent(
        "document-1:parent:0",
        0,
    )

    registry.register(parent)

    assert registry.get(
        "document-1:parent:0"
    ) == parent


def test_unknown_parent_returns_none():
    registry = ParentContextRegistry()

    assert registry.get(
        "unknown-parent"
    ) is None


def test_register_many_preserves_registry_order():
    parents = (
        make_parent("parent-0", 0),
        make_parent("parent-1", 1),
        make_parent("parent-2", 2),
    )

    registry = ParentContextRegistry(
        parents
    )

    assert registry.size == 3

    resolved = registry.resolve(
        [
            "parent-0",
            "parent-1",
            "parent-2",
        ]
    )

    assert resolved == parents


def test_resolve_preserves_requested_order():
    parents = (
        make_parent("parent-0", 0),
        make_parent("parent-1", 1),
        make_parent("parent-2", 2),
    )

    registry = ParentContextRegistry(
        parents
    )

    resolved = registry.resolve(
        [
            "parent-2",
            "parent-0",
            "parent-1",
        ]
    )

    assert [parent.parent_id for parent in resolved] == [
        "parent-2",
        "parent-0",
        "parent-1",
    ]


def test_resolve_deduplicates_parent_ids():
    parents = (
        make_parent("parent-0", 0),
        make_parent("parent-1", 1),
    )

    registry = ParentContextRegistry(
        parents
    )

    resolved = registry.resolve(
        [
            "parent-0",
            "parent-0",
            "parent-1",
            "parent-0",
        ]
    )

    assert [parent.parent_id for parent in resolved] == [
        "parent-0",
        "parent-1",
    ]


def test_resolve_ignores_unknown_parent_ids():
    parents = (
        make_parent("parent-0", 0),
        make_parent("parent-1", 1),
    )

    registry = ParentContextRegistry(
        parents
    )

    resolved = registry.resolve(
        [
            "unknown",
            "parent-1",
            "missing",
            "parent-0",
        ]
    )

    assert [parent.parent_id for parent in resolved] == [
        "parent-1",
        "parent-0",
    ]


def test_empty_resolution_returns_empty_tuple():
    registry = ParentContextRegistry()

    assert registry.resolve([]) == ()


def test_registering_duplicate_id_replaces_parent():
    registry = ParentContextRegistry()

    original = make_parent(
        "parent-0",
        0,
        "Original",
    )

    replacement = make_parent(
        "parent-0",
        0,
        "Replacement",
    )

    registry.register(original)
    registry.register(replacement)

    assert registry.size == 1

    assert registry.get(
        "parent-0"
    ) == replacement


def test_empty_parent_id_is_rejected():
    registry = ParentContextRegistry()

    parent = make_parent(
        "",
        0,
    )

    try:
        registry.register(parent)
    except ValueError as exc:
        assert str(exc) == (
            "parent.parent_id must not be empty"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_clear_removes_all_parents():
    registry = ParentContextRegistry(
        (
            make_parent("parent-0", 0),
            make_parent("parent-1", 1),
        )
    )

    assert registry.size == 2

    registry.clear()

    assert registry.size == 0

    assert registry.get(
        "parent-0"
    ) is None