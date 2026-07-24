from dataclasses import dataclass


@dataclass
class RetrievalRequest:
    query: str
    k: int = 3