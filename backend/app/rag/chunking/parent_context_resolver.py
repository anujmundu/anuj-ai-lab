from __future__ import annotations

from dataclasses import dataclass

from app.rag.parent_child import ParentChunk
from app.rag.parent_context import (
    ParentContextRegistry,
    parent_context_registry,
)
from app.rag.retrieval_models import RetrievalResult


@dataclass(frozen=True, slots=True)
class ResolvedParentContext:
    """
    Parent context resolved from retrieved child results.

    The original retrieval results are not modified.
    """

    parent: ParentChunk

    child_ids: tuple[str, ...]


class ParentContextResolver:
    """
    Resolves parent context for retrieved child chunks.

    This component sits between retrieval and context construction.

    Responsibilities:
    - Read parent_id from RetrievalResult metadata.
    - Resolve parents through ParentContextRegistry.
    - Deduplicate parents.
    - Preserve first-seen retrieval order.
    - Track which retrieved children contributed to each parent.
    - Ignore children without parent IDs.
    - Ignore unknown parent IDs safely.

    It does not perform retrieval and does not mutate
    RetrievalResult instances.
    """

    def __init__(
        self,
        registry: ParentContextRegistry,
    ) -> None:
        self.registry = registry

    def resolve(
        self,
        results: list[RetrievalResult]
        | tuple[RetrievalResult, ...],
    ) -> tuple[ResolvedParentContext, ...]:
        """
        Resolve parent context from retrieved results.

        Parent ordering follows the first occurrence of each
        parent_id in the retrieval results.

        Repeated children belonging to the same parent are
        grouped under one resolved parent.
        """

        grouped_child_ids: dict[str, list[str]] = {}
        ordered_parent_ids: list[str] = []
        seen_parent_ids: set[str] = set()

        for result in results:
            parent_id = result.parent_id

            if not parent_id:
                continue

            child_id = result.child_id or result.chunk_id

            if parent_id not in seen_parent_ids:
                seen_parent_ids.add(parent_id)
                ordered_parent_ids.append(parent_id)

            grouped_child_ids.setdefault(
                parent_id,
                [],
            ).append(child_id)

        resolved: list[ResolvedParentContext] = []

        for parent_id in ordered_parent_ids:
            parent = self.registry.get(parent_id)

            if parent is None:
                continue

            resolved.append(
                ResolvedParentContext(
                    parent=parent,
                    child_ids=tuple(
                        grouped_child_ids[parent_id]
                    ),
                )
            )

        return tuple(resolved)


def resolve_parent_context(
    results: list[RetrievalResult]
    | tuple[RetrievalResult, ...],
    *,
    registry: ParentContextRegistry,
) -> tuple[ResolvedParentContext, ...]:
    """
    Functional convenience wrapper around ParentContextResolver.
    """

    resolver = ParentContextResolver(
        registry=registry,
    )

    return resolver.resolve(results)


parent_context_resolver = ParentContextResolver(
    registry=parent_context_registry,
)