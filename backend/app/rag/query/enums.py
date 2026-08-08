from enum import Enum


class QueryIntent(str, Enum):
    DEFINITION = "definition"
    FACTUAL = "factual"
    EXPLANATION = "explanation"
    COMPARISON = "comparison"
    PROCEDURE = "procedure"
    RESEARCH = "research"
    UNKNOWN = "unknown"


class QueryComplexity(str, Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class QueryAmbiguity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"