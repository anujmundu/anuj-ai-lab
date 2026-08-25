from __future__ import annotations

from app.rag.graph.entity_extractor import entity_extractor
from app.rag.graph.graph_store import (
    KnowledgeGraphStore,
    knowledge_graph_store,
)
from app.rag.graph.models import GraphContext


class GraphRetriever:
    """
    Coordinates entity-relation extraction, graph indexing,
    and multi-hop graph retrieval.
    """

    def __init__(
        self,
        store: KnowledgeGraphStore | None = None,
    ):
        self.store = store or knowledge_graph_store

    def index_text(self, text: str) -> int:
        """Extract and index entities and relations from text into graph store."""
        entities, relations = entity_extractor.extract(text)
        for entity in entities:
            self.store.add_entity(entity)
        for relation in relations:
            self.store.add_relation(relation)
        return len(relations)

    def retrieve(
        self,
        query: str,
        max_hops: int = 2,
    ) -> GraphContext:
        """
        Extract query seed entities and traverse the knowledge graph
        to retrieve relevant relational context.
        """
        query_entities, _ = entity_extractor.extract(query)
        if not query_entities:
            return GraphContext()

        seed_names = [e.name for e in query_entities]
        entities, relations = self.store.get_subgraph(
            seed_names,
            max_hops=max_hops,
        )

        return GraphContext(
            entities=entities,
            relations=relations,
        )


graph_retriever = GraphRetriever()
