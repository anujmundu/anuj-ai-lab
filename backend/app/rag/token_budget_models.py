from __future__ import annotations

from dataclasses import dataclass, field

from app.rag.prompt_optimizer_models import PromptComponent

from app.rag.enums import AllocationStatus

@dataclass(slots=True)
class TokenAllocation:
    """
    Token allocation information for a single prompt component.
    """

    component: PromptComponent

    required_tokens: int
    allocated_tokens: int

    overflow_tokens: int = 0

    truncated: bool = False
    
    status: AllocationStatus = AllocationStatus.FIT

    @property
    def remaining_tokens(self) -> int:
        """
        Number of unused allocated tokens.
        """

        return max(
            0,
            self.allocated_tokens - self.required_tokens,
        )

    @property
    def utilization(self) -> float:
        """
        Allocation utilization in the range [0.0, 1.0].
        """

        if self.allocated_tokens == 0:
            return 0.0

        return min(
            1.0,
            self.required_tokens / self.allocated_tokens,
        )


@dataclass(slots=True)
class TokenBudget:
    """
    Overall token budget for a prompt.
    """

    context_window: int

    reserved_output_tokens: int

    available_input_tokens: int

    used_input_tokens: int

    remaining_input_tokens: int

    utilization: float


@dataclass(slots=True)
class TokenBudgetResult:
    """
    Result returned by the Token Budget Manager.
    """

    budget: TokenBudget

    allocations: list[TokenAllocation] = field(
        default_factory=list,
    )

    overflow_detected: bool = False

    recommendations: list[str] = field(
        default_factory=list,
    )

    @property
    def total_overflow_tokens(self) -> int:
        """
        Total number of tokens exceeding the allocated budget.
        """

        return sum(
            allocation.overflow_tokens
            for allocation in self.allocations
        )

    @property
    def truncated_component_count(self) -> int:
        """
        Number of components marked for truncation.
        """

        return sum(
            allocation.truncated
            for allocation in self.allocations
        )


    @property
    def components(self) -> list[PromptComponent]:
        """
        Return the prompt components after token allocation.

        This allows downstream pipeline stages (such as the
        PromptRenderer) to operate directly on PromptComponent
        objects without needing to understand TokenAllocation.
        """

        return [
            allocation.component
            for allocation in self.allocations
        ]
        