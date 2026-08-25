from __future__ import annotations

import re
from app.rag.graph.models import Entity, Relation


class EntityExtractor:
    """
    Extracts entities and relational triplets from text chunks.
    """

    RELATION_PATTERNS = [
        # X is / was a Y
        (r"(?i)([A-Z][a-zA-Z0-9_]+)\s+(?:is|was|are|were)\s+(?:an?|the)\s+([a-zA-Z0-9_\s]{3,30}?)(?:\.|\,|$)", "is_a"),
        # X stores Y
        (r"(?i)([A-Z][a-zA-Z0-9_]+)\s+stores\s+([a-zA-Z0-9_\s]{3,30}?)(?:\.|\,|$)", "stores"),
        # X uses / utilizes Y
        (r"(?i)([A-Z][a-zA-Z0-9_]+)\s+(?:uses|utilizes|leverages)\s+([a-zA-Z0-9_\s]{3,30}?)(?:\.|\,|$)", "uses"),
        # X connects to / integrates with Y
        (r"(?i)([A-Z][a-zA-Z0-9_]+)\s+(?:connects to|integrates with)\s+([a-zA-Z0-9_\s]{3,30}?)(?:\.|\,|$)", "connects_to"),
        # X generates / produces Y
        (r"(?i)([A-Z][a-zA-Z0-9_]+)\s+(?:generates|produces|creates)\s+([a-zA-Z0-9_\s]{3,30}?)(?:\.|\,|$)", "generates"),
        # X contains / includes Y
        (r"(?i)([A-Z][a-zA-Z0-9_]+)\s+(?:contains|includes)\s+([a-zA-Z0-9_\s]{3,30}?)(?:\.|\,|$)", "contains"),
    ]

    def extract(self, text: str) -> tuple[list[Entity], list[Relation]]:
        entities_dict: dict[str, Entity] = {}
        relations: list[Relation] = []

        # 1. Regex pattern triplet matching
        for pattern, rel_type in self.RELATION_PATTERNS:
            matches = re.finditer(pattern, text)
            for match in matches:
                source = match.group(1).strip()
                target = match.group(2).strip()

                if len(source) > 1 and len(target) > 1:
                    entities_dict[source.lower()] = Entity(
                        name=source,
                        entity_type="concept",
                    )
                    entities_dict[target.lower()] = Entity(
                        name=target,
                        entity_type="concept",
                    )
                    relations.append(
                        Relation(
                            source=source,
                            relation=rel_type,
                            target=target,
                            context=match.group(0).strip(),
                        )
                    )

        # 2. Extract capitalized proper nouns / components
        proper_nouns = re.findall(r"\b[A-Z][a-zA-Z0-9_]{2,}\b", text)
        for noun in proper_nouns:
            if noun.lower() not in entities_dict and noun not in {"The", "This", "That", "When", "What", "Where", "Why", "How"}:
                entities_dict[noun.lower()] = Entity(
                    name=noun,
                    entity_type="entity",
                )

        return list(entities_dict.values()), relations


entity_extractor = EntityExtractor()
