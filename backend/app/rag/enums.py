from enum import Enum


class PromptComponentType(str, Enum):
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


class AllocationStrategy(str, Enum):
    """
    Token allocation strategies.
    """

    PRIORITY = "priority"


class AllocationStatus(str, Enum):
    """
    Result of allocating tokens to a component.
    """

    FIT = "fit"
    OVERFLOW = "overflow"
    TRUNCATED = "truncated"