from __future__ import annotations

from dataclasses import dataclass

from app.rag.prompt_optimizer_models import (
    PromptAnalysis,
    PromptOptimizationResult,
)
from app.rag.token_budget_models import TokenBudgetResult


@dataclass(slots=True)
class PromptPipelineResult:
    """
    Complete output of the Prompt Intelligence pipeline.
    """

    prompt: str

    analysis: PromptAnalysis

    optimization: PromptOptimizationResult

    budget: TokenBudgetResult
    
    quality: dict 