from __future__ import annotations

from collections import defaultdict, deque
from app.rag.graph.models import Entity, Relation


class KnowledgeGraphStore:
    """
    Lightweight, fast in-memory and persistent Knowledge Graph store
    supporting multi-hop subgraph extraction and path finding.
    """

    def __init__(self):
        self._entities: dict[str, Entity] = {}
        # source_lower -> list of outgoing Relations
        self._adjacency: dict[str, list[Relation]] = defaultdict(list)
        # target_lower -> list of incoming Relations
        self._reverse_adj: dict[str, list[Relation]] = defaultdict(list)

    def add_entity(self, entity: Entity) -> None:
        key = entity.name.lower()
        if key not in self._entities:
            self._entities[key] = entity

    def add_relation(self, relation: Relation) -> None:
        src_key = relation.source.lower()
        tgt_key = relation.target.lower()

        if src_key not in self._entities:
            self.add_entity(Entity(name=relation.source))
        if tgt_key not in self._entities:
            self.add_entity(Entity(name=relation.target))

        self._adjacency[src_key].append(relation)
        self._reverse_adj[tgt_key].append(relation)

    def get_entity(self, name: str) -> Entity | None:
        return self._entities.get(name.lower())

    def get_neighbors(
        self,
        entity_name: str,
        max_hops: int = 1,
    ) -> list[Relation]:
        start_key = entity_name.lower()
        if start_key not in self._entities and start_key not in self._adjacency:
            return []

        visited = set([start_key])
        queue = deque([(start_key, 0)])
        result_relations: list[Relation] = []

        while queue:
            current, hops = queue.popleft()
            if hops >= max_hops:
                continue

            outgoing = self._adjacency.get(current, [])
            for rel in outgoing:
                result_relations.append(rel)
                tgt_key = rel.target.lower()
                if tgt_key not in visited:
                    visited.add(tgt_key)
                    queue.append((tgt_key, hops + 1))

            incoming = self._reverse_adj.get(current, [])
            for rel in incoming:
                if rel not in result_relations:
                    result_relations.append(rel)
                src_key = rel.source.lower()
                if src_key not in visited:
                    visited.add(src_key)
                    queue.append((src_key, hops + 1))

        return result_relations

    def get_subgraph(
        self,
        seed_entities: list[str],
        max_hops: int = 2,
    ) -> tuple[list[Entity], list[Relation]]:
        collected_relations: list[Relation] = []
        collected_entities: set[str] = set()

        for seed in seed_entities:
            relations = self.get_neighbors(seed, max_hops=max_hops)
            for r in relations:
                collected_relations.append(r)
                collected_entities.add(r.source.lower())
                collected_entities.add(r.target.lower())

        entities = [
            self._entities[key]
            for key in collected_entities
            if key in self._entities
        ]
        return entities, collected_relations

    def find_paths(
        self,
        source: str,
        target: str,
        max_depth: int = 3,
    ) -> list[list[Relation]]:
        src_key = source.lower()
        tgt_key = target.lower()

        if src_key not in self._entities or tgt_key not in self._entities:
            return []

        paths: list[list[Relation]] = []
        # BFS tracking path of relations
        queue = deque([([src_key], [])])

        while queue:
            node_path, rel_path = queue.popleft()
            current = node_path[-1]

            if current == tgt_key and rel_path:
                paths.append(rel_path)
                continue

            if len(node_path) > max_depth:
                continue

            for rel in self._adjacency.get(current, []):
                next_key = rel.target.lower()
                if next_key not in node_path:
                    queue.append((node_path + [next_key], rel_path + [rel]))

        return paths

    def clear(self) -> None:
        self._entities.clear()
        self._adjacency.clear()
        self._reverse_adj.clear()


knowledge_graph_store = KnowledgeGraphStore()
