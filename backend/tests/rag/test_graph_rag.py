from app.rag.graph.entity_extractor import EntityExtractor
from app.rag.graph.graph_store import KnowledgeGraphStore
from app.rag.graph.graph_retriever import GraphRetriever
from app.rag.graph.models import Entity, Relation


def test_entity_extractor_triplets():
    extractor = EntityExtractor()
    text = (
        "ChromaDB stores vector embeddings for fast retrieval. "
        "FastAPI connects to SQLite databases. "
        "SentenceTransformers produces dense embeddings."
    )

    entities, relations = extractor.extract(text)

    assert len(entities) > 0
    assert len(relations) >= 2

    relation_types = [r.relation for r in relations]
    assert "stores" in relation_types or "connects_to" in relation_types or "produces" in relation_types


def test_knowledge_graph_store_traversal():
    store = KnowledgeGraphStore()

    store.add_relation(Relation(source="FastAPI", relation="connects_to", target="SQLite"))
    store.add_relation(Relation(source="SQLite", relation="stores", target="ChatMessages"))
    store.add_relation(Relation(source="ChatMessages", relation="contains", target="Citations"))

    # 1-hop neighbors from FastAPI
    neighbors_1hop = store.get_neighbors("FastAPI", max_hops=1)
    assert any(r.target == "SQLite" for r in neighbors_1hop)

    # 2-hop subgraph from FastAPI
    entities, relations = store.get_subgraph(["FastAPI"], max_hops=2)
    entity_names = [e.name for e in entities]
    assert "FastAPI" in entity_names
    assert "SQLite" in entity_names
    assert "ChatMessages" in entity_names

    # Multi-hop path finding from FastAPI to Citations
    paths = store.find_paths("FastAPI", "Citations", max_depth=3)
    assert len(paths) >= 1
    assert len(paths[0]) == 3  # FastAPI -> SQLite -> ChatMessages -> Citations


def test_graph_retriever_pipeline():
    store = KnowledgeGraphStore()
    retriever = GraphRetriever(store=store)

    doc_text = "ChromaDB is a vector database. ChromaDB stores vector embeddings."
    indexed_count = retriever.index_text(doc_text)
    assert indexed_count >= 1

    # Query matching seed entity
    graph_context = retriever.retrieve("What does ChromaDB store?")
    assert len(graph_context.relations) >= 1

    formatted = graph_context.format_context()
    assert "KNOWLEDGE GRAPH RELATIONS:" in formatted
    assert "ChromaDB" in formatted
