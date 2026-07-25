from dataclasses import dataclass
    
@dataclass
class QueryAnalysis:
    """
    Structural analysis of an incoming query.

    This analysis is deterministic and does not
    require an LLM.
    """

    token_count: int

    character_count: int

    word_count: int

    contains_question_word: bool

    contains_number: bool

    contains_boolean_operator: bool

    contains_temporal_reference: bool

    contains_comparison: bool

    estimated_complexity: str