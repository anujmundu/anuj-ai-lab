from enum import Enum, StrEnum


class PromptComponentType(StrEnum):
    """
    Logical sections of a prompt.
    """

    SYSTEM = "system"
    CONTEXT = "context"
    MEMORY = "memory"
    CONVERSATION = "conversation"
    QUESTION = "question"
    EXAMPLES = "examples"
    TOOLS = "tools"


class AllocationStrategy(StrEnum):
    """
    Token allocation strategies.
    """

    PRIORITY = "priority"


class AllocationStatus(StrEnum):
    """
    Result of allocating tokens to a component.
    """

    FIT = "fit"
    OVERFLOW = "overflow"
    TRUNCATED = "truncated"


class PerformanceStageName(StrEnum):
    """
    Standardized names for performance profiling stages.

    These values are used throughout the Performance Profiler
    and diagnostics to ensure consistent stage naming.
    """

    RETRIEVAL = "retrieval"

    QUERY_EMBEDDING = "query_embedding"

    VECTOR_SEARCH = "vector_search"

    BM25_SEARCH = "bm25_search"

    RANK_FUSION = "rank_fusion"

    SEMANTIC_RERANKER = "semantic_reranker"

    RETRIEVAL_FILTERING = "retrieval_filtering"

    CONTEXT_BUILDER = "context_builder"

    PROMPT_BUILDER = "prompt_builder"

    PROMPT_NORMALIZER = "prompt_normalizer"

    PROMPT_ANALYZER = "prompt_analyzer"

    PROMPT_OPTIMIZER = "prompt_optimizer"

    TOKEN_BUDGET = "token_budget"

    PROMPT_RENDERER = "prompt_renderer"

    LLM_GENERATION = "llm_generation"

    POST_PROCESSING = "post_processing"

    CITATION_PROCESSOR = "citation_processor"

    EVIDENCE_ALIGNMENT = "evidence_alignment"

    HALLUCINATION_DETECTION = "hallucination_detection"

    CONSISTENCY_ANALYSIS = "consistency_analysis"

    ANSWER_QUALITY = "answer_quality"
