from __future__ import annotations

from collections import OrderedDict

from app.rag.parent_child import ParentChunk


class ParentContextRegistry:
    """
    Deterministic registry for parent chunks.

    Parent chunks are context-bearing objects produced by the
    parent-child ingestion layer.

    Responsibilities:
    - Register parent chunks.
    - Resolve a parent by ID.
    - Resolve multiple parent IDs.
    - Preserve requested parent order.
    - Deduplicate repeated parent IDs.
    - Ignore unknown parent IDs safely.

    This component does not perform retrieval and does not
    modify the existing TextChunker or retrieval pipeline.
    """

    def __init__(
        self,
        parents: list[ParentChunk] | tuple[ParentChunk, ...] | None = None,
    ) -> None:

        self._parents: OrderedDict[str, ParentChunk] = OrderedDict()

        if parents:
            self.register_many(parents)

    # --------------------------------------------------
    # Registration
    # --------------------------------------------------

    def register(
        self,
        parent: ParentChunk,
    ) -> None:
        """
        Register one parent chunk.

        Re-registering the same parent ID replaces its value
        without changing its logical position.
        """

        if not parent.parent_id.strip():
            raise ValueError(
                "parent.parent_id must not be empty"
            )

        self._parents[parent.parent_id] = parent

    def register_many(
        self,
        parents: list[ParentChunk] | tuple[ParentChunk, ...],
    ) -> None:
        """
        Register multiple parent chunks in deterministic order.
        """

        for parent in parents:
            self.register(parent)

    # --------------------------------------------------
    # Lookup
    # --------------------------------------------------

    def get(
        self,
        parent_id: str,
    ) -> ParentChunk | None:
        """
        Return a parent by ID.

        Unknown IDs return None rather than raising.
        """

        return self._parents.get(parent_id)

    # --------------------------------------------------
    # Resolution
    # --------------------------------------------------

    def resolve(
        self,
        parent_ids: list[str] | tuple[str, ...],
    ) -> tuple[ParentChunk, ...]:
        """
        Resolve multiple parent IDs.

        Guarantees:
        - Input order is preserved.
        - Duplicate IDs are returned only once.
        - Unknown IDs are ignored.
        """

        resolved: list[ParentChunk] = []
        seen: set[str] = set()

        for parent_id in parent_ids:

            if parent_id in seen:
                continue

            seen.add(parent_id)

            parent = self.get(parent_id)

            if parent is None:
                continue

            resolved.append(parent)

        return tuple(resolved)

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    @property
    def size(self) -> int:
        """
        Number of registered parent chunks.
        """

        return len(self._parents)

    def clear(self) -> None:
        """
        Remove all registered parents.
        """

        self._parents.clear()


parent_context_registry = ParentContextRegistry()