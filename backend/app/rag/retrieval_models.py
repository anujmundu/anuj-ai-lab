from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RetrievalResult:
    """
    Internal representation of a retrieved document.

    This format is independent of ChromaDB and can be
    produced by any retrieval engine.
    """

    doc_id: str

    document: str

    metadata: dict[str, Any]

    semantic_score: float = 0.0

    keyword_score: float = 0.0

    combined_score: float = 0.0