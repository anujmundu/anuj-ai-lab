from __future__ import annotations

from dataclasses import dataclass, field
from app.rag.enums import PromptComponentType
from typing import List


@dataclass(slots=True)
class PromptComponent:
    """
    Represents a logical section of a prompt before it is rendered
    into the final prompt string.
    """

    component_type: PromptComponentType
    text: str

    tokens: int = 0
    characters: int = 0

    priority: int = 100
    required: bool = False

    def __post_init__(self) -> None:
        if self.characters == 0:
            self.characters = len(self.text)
            
    @property
    def estimated_tokens(self) -> int:
        """
        Returns the actual token count if available,
        otherwise estimates tokens from character count.
        """

        if self.tokens > 0:
            return self.tokens

        return max(1, self.characters // 4)


@dataclass(slots=True)
class PromptAnalysis:
    """Statistics describing a prompt."""

    total_tokens: int = 0
    total_characters: int = 0

    instruction_ratio: float = 0.0
    context_ratio: float = 0.0
    memory_ratio: float = 0.0
    conversation_ratio: float = 0.0
    question_ratio: float = 0.0

    largest_component: str = ""

    efficiency_score: float = 0.0
    redundancy_score: float = 0.0

    balanced: bool = True

    recommendations: List[str] = field(default_factory=list)


@dataclass(slots=True)
class PromptOptimization:
    """Describes one optimization that was applied."""

    rule_name: str
    description: str

    tokens_saved: int = 0


@dataclass(slots=True)
class PromptOptimizationResult:
    """
    Result returned by the Prompt Optimizer.
    """

    original_components: List[PromptComponent]
    optimized_components: List[PromptComponent]

    analysis_before: PromptAnalysis
    analysis_after: PromptAnalysis

    optimizations: List[PromptOptimization] = field(default_factory=list)

    tokens_saved: int = 0

    @property
    def optimization_count(self) -> int:
        return len(self.optimizations)