from __future__ import annotations

from app.rag.prompt_optimizer_models import PromptComponent
from app.rag.token_budget_config import TokenBudgetConfig
from app.rag.token_budget_models import (
    AllocationStatus,
    TokenAllocation,
    TokenBudget,
    TokenBudgetResult,
)


class TokenBudgetManager:
    """
    Determines how PromptComponents fit within the model's
    available context window.

    This class NEVER modifies PromptComponents.
    """

    def __init__(
        self,
        config: TokenBudgetConfig | None = None,
    ):
        self.config = config or TokenBudgetConfig()
        
    def _sort_components(
        self,
        components: list[PromptComponent],
    ) -> list[PromptComponent]:
        """
        Return prompt components ordered by allocation priority.

        Components with lower priority values are allocated first.
        """

        return sorted(
            components,
            key=lambda component: component.priority,
        )
        
    def _validate_components(
        self,
        components: list[PromptComponent],
    ) -> None:
        """
        Validate prompt components before token allocation.
        """

        for component in components:

            if component.estimated_tokens < 0:
                raise ValueError(
                    "Component estimated_tokens cannot be negative."
                )

            if component.priority < 0:
                raise ValueError(
                    "Component priority cannot be negative."
                )

    def allocate(
        self,
        components: list[PromptComponent],
        *,
        context_window: int | None = None,
        reserved_output_tokens: int | None = None,
    ) -> TokenBudgetResult:

        if not self.config.enable_budgeting:

            context = (
                context_window
                or self.config.default_context_window
            )

            reserved = (
                reserved_output_tokens
                or self.config.default_reserved_output_tokens
            )

            available = max(
                0,
                context - reserved,
            )

            budget = TokenBudget(
                context_window=context,
                reserved_output_tokens=reserved,
                available_input_tokens=available,
                used_input_tokens=0,
                remaining_input_tokens=available,
                utilization=0.0,
            )

            return TokenBudgetResult(
                budget=budget,
            )

        context = (
            context_window
            or self.config.default_context_window
        )

        reserved = max(
            reserved_output_tokens
            or self.config.default_reserved_output_tokens,
            self.config.minimum_reserved_output_tokens,
        )

        available = max(
            0,
            context - reserved,
        )

        allocations: list[TokenAllocation] = []

        remaining_budget = available

        total_required = 0
        total_allocated = 0

        overflow_detected = False

        recommendations: list[str] = []
        
        self._validate_components(components)
        
        # Allocate components in deterministic priority order.
        components = self._sort_components(components)

        for component in components:

            required = component.estimated_tokens

            allocated = min(
                required,
                remaining_budget,
            )

            overflow = required - allocated

            remaining_budget -= allocated

            if overflow == 0:

                status = AllocationStatus.FIT

            elif allocated == 0:

                status = AllocationStatus.TRUNCATED

                overflow_detected = True

            else:

                status = AllocationStatus.OVERFLOW

                overflow_detected = True

            allocation = TokenAllocation(
                component=component,
                required_tokens=required,
                allocated_tokens=allocated,
                overflow_tokens=overflow,
                truncated=allocated < required,
                status=status,
            )

            allocations.append(allocation)

            total_required += required

            total_allocated += allocated

        remaining = remaining_budget

        utilization = 0.0

        if available > 0:
            utilization = min(
                1.0,
                total_allocated / available,
            )

        if overflow_detected:
            recommendations.append(
                "Prompt exceeds the available input token budget."
            )

            recommendations.append(
                "Consider context compression or memory pruning."
            )

        budget = TokenBudget(
            context_window=context,
            reserved_output_tokens=reserved,
            available_input_tokens=available,
            used_input_tokens=total_allocated,
            remaining_input_tokens=remaining,
            utilization=utilization,
        )

        return TokenBudgetResult(
            budget=budget,
            allocations=allocations,
            overflow_detected=overflow_detected,
            recommendations=recommendations,
        )


token_budget_manager = TokenBudgetManager()