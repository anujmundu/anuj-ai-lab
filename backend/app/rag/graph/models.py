from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class Entity:
    """Represents a named entity in the knowledge graph."""

    name: str
    entity_type: str = "concept"
    description: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class Relation:
    """Represents a directed relationship between two entities."""

    source: str
    relation: str
    target: str
    weight: float = 1.0
    context: str = ""


@dataclass(slots=True)
class GraphContext:
    """Formatted graph retrieval context for RAG prompts."""

    entities: list[Entity] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    summary: str = ""

    def format_context(self) -> str:
        """Format the graph context into human-readable prompt text."""
        if not self.relations and not self.entities:
            return ""

        lines = ["KNOWLEDGE GRAPH RELATIONS:"]
        for r in self.relations:
            lines.append(f"• ({r.source}) -[{r.relation}]-> ({r.target})")

        if self.entities:
            lines.append("\nKEY ENTITIES:")
            for e in self.entities:
                desc = f": {e.description}" if e.description else ""
                lines.append(f"• {e.name} ({e.entity_type}){desc}")

        return "\n".join(lines)
