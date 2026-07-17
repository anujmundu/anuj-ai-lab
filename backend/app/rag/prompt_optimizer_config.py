from pydantic import BaseModel, Field


class PromptOptimizerConfig(BaseModel):
    """
    Configuration for PromptOptimizer.
    """

    enable_optimization: bool = True

    normalize_blank_lines: bool = True

    remove_trailing_whitespace: bool = True

    collapse_multiple_spaces: bool = False

    max_prompt_characters: int = Field(
        default=12000,
        ge=1,
    )