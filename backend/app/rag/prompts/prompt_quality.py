from app.rag.prompt_quality_config import (
    PromptQualityConfig,
)

from app.rag.prompt_optimizer_models import (
    PromptAnalysis,
    PromptOptimizationResult,
)

from app.rag.token_budget_models import (
    TokenBudgetResult,
)


class PromptQuality:
    """
    Computes overall prompt quality from the Prompt
    Intelligence pipeline.

    Responsibilities
    ----------------
    • Summarize PromptAnalysis
    • Summarize PromptOptimizationResult
    • Summarize TokenBudgetResult
    """

    def __init__(
        self,
        config: PromptQualityConfig | None = None,
    ):
        self.config = (
            config
            or PromptQualityConfig()
        )

    def analyze(
        self,
        *,
        analysis: PromptAnalysis,
        optimization: PromptOptimizationResult,
        budget: TokenBudgetResult,
    ) -> dict:

        if not self.config.enabled:
            return {}

        efficiency = analysis.efficiency_score

        if efficiency >= 0.80:
            efficiency_label = "Excellent"

        elif efficiency >= 0.60:
            efficiency_label = "Good"

        elif efficiency >= 0.40:
            efficiency_label = "Fair"

        else:
            efficiency_label = "Poor"

        return {

            # -----------------------------
            # Prompt analysis
            # -----------------------------

            "total_tokens": analysis.total_tokens,

            "total_characters": analysis.total_characters,

            "instruction_ratio": round(
                analysis.instruction_ratio,
                3,
            ),

            "context_ratio": round(
                analysis.context_ratio,
                3,
            ),

            "memory_ratio": round(
                analysis.memory_ratio,
                3,
            ),

            "conversation_ratio": round(
                analysis.conversation_ratio,
                3,
            ),

            "question_ratio": round(
                analysis.question_ratio,
                3,
            ),

            "largest_component": (
                analysis.largest_component
            ),

            "balanced": analysis.balanced,

            "efficiency_score": round(
                analysis.efficiency_score,
                3,
            ),

            "redundancy_score": round(
                analysis.redundancy_score,
                3,
            ),

            "prompt_efficiency": (
                efficiency_label
            ),

            "recommendations": (
                analysis.recommendations
            ),

            # -----------------------------
            # Optimization
            # -----------------------------

            "optimization_count": (
                optimization.optimization_count
            ),

            "tokens_saved": (
                optimization.tokens_saved
            ),

            # -----------------------------
            # Token budget
            # -----------------------------

            "context_window": (
                budget.budget.context_window
            ),

            "reserved_output_tokens": (
                budget.budget.reserved_output_tokens
            ),

            "available_input_tokens": (
                budget.budget.available_input_tokens
            ),

            "used_input_tokens": (
                budget.budget.used_input_tokens
            ),

            "remaining_input_tokens": (
                budget.budget.remaining_input_tokens
            ),

            "budget_utilization": round(
                budget.budget.utilization,
                3,
            ),

            "overflow_detected": (
                budget.overflow_detected
            ),

            "overflow_tokens": (
                budget.total_overflow_tokens
            ),

            "truncated_components": (
                budget.truncated_component_count
            ),
        }


prompt_quality = PromptQuality()