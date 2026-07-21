from pydantic import BaseModel, ConfigDict, Field


class PromptOptimizerConfig(BaseModel):
    """
    Configuration for the Prompt Optimizer.

    The optimizer operates on structured PromptComponents rather than
    raw prompt strings. It applies deterministic optimization rules
    while preserving the semantic meaning of the prompt.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )

    # ------------------------------------------------------------------
    # Master Switch
    # ------------------------------------------------------------------

    enable_optimization: bool = True

    # ------------------------------------------------------------------
    # Optimization Rules
    # ------------------------------------------------------------------

    remove_duplicate_components: bool = True

    remove_empty_components: bool = True

    sort_by_priority: bool = True

    preserve_required_components: bool = True

    # ------------------------------------------------------------------
    # Safety Limits
    # ------------------------------------------------------------------

    minimum_component_characters: int = Field(
        default=1,
        ge=0,
        description="Minimum characters required for a component to be retained.",
    )

    maximum_component_count: int = Field(
        default=100,
        ge=1,
        description="Maximum number of prompt components allowed.",
    )

    # ------------------------------------------------------------------
    # Future Features (Reserved)
    # ------------------------------------------------------------------

    enable_semantic_deduplication: bool = False

    enable_context_compression: bool = False

    enable_instruction_merging: bool = False

    enable_memory_pruning: bool = False