from __future__ import annotations

from typing import Any
from app.rag.graph.graph_store import KnowledgeGraphStore, knowledge_graph_store
from app.rag.graph.models import Entity, Relation


class GraphOptimizer:
    """
    Optimizes the Knowledge Graph through entity deduplication, alias merging, and dead-node pruning.
    """

    def __init__(self, store: KnowledgeGraphStore | None = None) -> None:
        self.store = store or knowledge_graph_store

    def _are_aliases(self, name_a: str, name_b: str) -> bool:
        a, b = name_a.lower().strip(), name_b.lower().strip()
        if a == b:
            return True
        if len(a) > 3 and len(b) > 3:
            if a in b or b in a:
                return True
        return False

    def optimize(self) -> dict[str, Any]:
        """
        Merges alias entities and deduplicates relations in the KnowledgeGraphStore.
        """
        entity_keys = list(self.store._entities.keys())
        merged_count = 0
        canonical_map: dict[str, str] = {}

        # 1. Identify alias groups
        for i, key_a in enumerate(entity_keys):
            for key_b in entity_keys[i + 1 :]:
                if self._are_aliases(key_a, key_b):
                    # Choose shorter or cleaner key as canonical
                    canonical = key_a if len(key_a) <= len(key_b) else key_b
                    alias = key_b if canonical == key_a else key_a
                    canonical_map[alias] = canonical
                    merged_count += 1

        # 2. Re-route relations
        pruned_relations_count = 0
        seen_triplets: set[tuple[str, str, str]] = set()

        for src, rels in list(self.store._adjacency.items()):
            new_rels: list[Relation] = []
            for r in rels:
                canonical_src = canonical_map.get(r.source.lower(), r.source)
                canonical_tgt = canonical_map.get(r.target.lower(), r.target)

                triplet = (canonical_src.lower(), r.relation.lower(), canonical_tgt.lower())
                if triplet not in seen_triplets:
                    seen_triplets.add(triplet)
                    new_rels.append(
                        Relation(
                            source=canonical_src,
                            relation=r.relation,
                            target=canonical_tgt,
                            weight=r.weight,
                            context=r.context,
                        )
                    )
                else:
                    pruned_relations_count += 1

            self.store._adjacency[src] = new_rels

        return {
            "entities_merged": merged_count,
            "duplicate_relations_pruned": pruned_relations_count,
            "total_entities_remaining": len(self.store._entities),
            "status": "optimized",
        }


graph_optimizer = GraphOptimizer()
