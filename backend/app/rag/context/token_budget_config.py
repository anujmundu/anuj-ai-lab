from pydantic import BaseModel, ConfigDict, Field
from app.rag.enums import AllocationStrategy

class TokenBudgetConfig(BaseModel):
    """
    Configuration for the Token Budget Manager.

    The manager determines how the available context window
    is allocated across PromptComponents before prompt rendering.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    # ------------------------------------------------------------------
    # Master Switch
    # ------------------------------------------------------------------

    enable_budgeting: bool = Field(
        default=True,
    )

    # ------------------------------------------------------------------
    # Model Limits
    # ------------------------------------------------------------------

    default_context_window: int = Field(
        default=32768,
        ge=1024,
        description="Maximum context window supported by the model.",
    )

    default_reserved_output_tokens: int = Field(
        default=2048,
        ge=128,
        description="Tokens reserved for model generation.",
    )

    minimum_reserved_output_tokens: int = Field(
        default=512,
        ge=128,
        description="Minimum output tokens that must always remain available.",
    )

    # ------------------------------------------------------------------
    # Allocation Strategy
    # ------------------------------------------------------------------

    allocation_strategy: AllocationStrategy = Field(
        default=AllocationStrategy.PRIORITY,
        description="Token allocation strategy.",
    )

    # ------------------------------------------------------------------
    # Overflow Handling
    # ------------------------------------------------------------------

    allow_component_overflow: bool = Field(
        default=True,
    )

    preserve_required_components: bool = Field(
        default=True,
    )

    # ------------------------------------------------------------------
    # Future Features
    # ------------------------------------------------------------------

    enable_dynamic_budgeting: bool = Field(
        default=False,
    )

    enable_context_compression: bool = Field(
        default=False,
    )

    enable_memory_pruning: bool = Field(
        default=False,
    )

    enable_adaptive_allocation: bool = Field(
        default=False,
    )