from app.rag.graph.graph_optimizer import GraphOptimizer
from app.rag.graph.graph_store import KnowledgeGraphStore
from app.rag.graph.models import Entity, Relation


def test_graph_optimizer_alias_merging():
    store = KnowledgeGraphStore()
    store.add_entity(Entity(name="ChromaDB", entity_type="TECHNOLOGY"))
    store.add_entity(Entity(name="Chroma", entity_type="TECHNOLOGY"))
    store.add_relation(Relation(source="ChromaDB", relation="provides", target="vector search"))
    store.add_relation(Relation(source="Chroma", relation="provides", target="vector search"))

    optimizer = GraphOptimizer(store=store)
    result = optimizer.optimize()

    assert result["status"] == "optimized"
    assert result["entities_merged"] >= 1
    assert result["duplicate_relations_pruned"] >= 1
