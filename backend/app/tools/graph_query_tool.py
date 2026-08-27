from __future__ import annotations

from typing import Any
from app.rag.graph.graph_store import knowledge_graph_store
from app.tools.base import BaseTool
from app.tools.models import ToolParameter


class KnowledgeGraphQueryTool(BaseTool):
    """
    Queries entities, relations, and multi-hop pathways in the Knowledge Graph.
    """

    name = "knowledge_graph_query"
    description = "Queries the Knowledge Graph for entities, related concepts, and multi-hop paths."
    parameters = [
        ToolParameter(
            name="query_type",
            type="string",
            description="Type of graph query: 'neighbors', 'path', 'subgraph'",
            required=True,
        ),
        ToolParameter(
            name="entity_name",
            type="string",
            description="The primary entity to query (for 'neighbors' or 'subgraph').",
            required=False,
            default="",
        ),
        ToolParameter(
            name="target_entity",
            type="string",
            description="The target entity for path-finding (when query_type is 'path').",
            required=False,
            default="",
        ),
        ToolParameter(
            name="max_hops",
            type="integer",
            description="Maximum traversal hops (default 2).",
            required=False,
            default=2,
        ),
    ]

    def _run(
        self,
        query_type: str = "neighbors",
        entity_name: str = "",
        target_entity: str = "",
        max_hops: int = 2,
        **kwargs: Any,
    ) -> Any:
        if query_type == "neighbors":
            if not entity_name:
                raise ValueError("entity_name is required for neighbors query")
            relations = knowledge_graph_store.get_neighbors(entity_name, max_hops=max_hops)
            return [
                {
                    "source": r.source,
                    "relation": r.relation,
                    "target": r.target,
                    "context": r.context,
                }
                for r in relations
            ]

        elif query_type == "path":
            if not entity_name or not target_entity:
                raise ValueError("Both entity_name and target_entity are required for path query")
            paths = knowledge_graph_store.find_paths(entity_name, target_entity, max_depth=max_hops)
            serialized_paths = []
            for path in paths:
                serialized_paths.append([
                    {"source": r.source, "relation": r.relation, "target": r.target}
                    for r in path
                ])
            return {"paths_found": len(serialized_paths), "paths": serialized_paths}

        elif query_type == "subgraph":
            if not entity_name:
                raise ValueError("entity_name is required for subgraph query")
            entities, relations = knowledge_graph_store.get_subgraph([entity_name], max_hops=max_hops)
            return {
                "entities": [e.name for e in entities],
                "relations": [
                    {"source": r.source, "relation": r.relation, "target": r.target}
                    for r in relations
                ],
            }

        else:
            raise ValueError(f"Unknown query_type '{query_type}'. Supported: 'neighbors', 'path', 'subgraph'")


knowledge_graph_query_tool = KnowledgeGraphQueryTool()
