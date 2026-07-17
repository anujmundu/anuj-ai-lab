import re

from app.rag.prompt_optimizer_config import PromptOptimizerConfig


class PromptOptimizer:
    """
    Performs lightweight prompt normalization before
    sending prompts to the language model.

    Responsibilities
    ----------------
    - Normalize blank lines
    - Remove trailing whitespace
    - Optionally collapse repeated spaces
    - Enforce maximum prompt size

    This class intentionally performs NO diagnostics.
    """

    def __init__(
        self,
        config: PromptOptimizerConfig | None = None,
    ):
        self.config = config or PromptOptimizerConfig()

    def optimize(
        self,
        prompt: str,
    ) -> str:
        """
        Optimize a prompt before sending it to the LLM.
        """

        if not self.config.enable_optimization:
            return prompt

        optimized = prompt

        if self.config.remove_trailing_whitespace:
            optimized = self._remove_trailing_whitespace(
                optimized,
            )

        if self.config.normalize_blank_lines:
            optimized = self._normalize_blank_lines(
                optimized,
            )

        if self.config.collapse_multiple_spaces:
            optimized = self._collapse_multiple_spaces(
                optimized,
            )

        optimized = self._trim_prompt(
            optimized,
        )

        return optimized

    def _remove_trailing_whitespace(
        self,
        prompt: str,
    ) -> str:
        """
        Remove trailing whitespace from every line.
        """

        return "\n".join(
            line.rstrip()
            for line in prompt.splitlines()
        )

    def _normalize_blank_lines(
        self,
        prompt: str,
    ) -> str:
        """
        Collapse 3+ blank lines into exactly 2.
        """

        return re.sub(
            r"\n{3,}",
            "\n\n",
            prompt,
        )

    def _collapse_multiple_spaces(
        self,
        prompt: str,
    ) -> str:
        """
        Collapse repeated spaces into a single space.
        """

        return re.sub(
            r"[ ]{2,}",
            " ",
            prompt,
        )

    def _trim_prompt(
        self,
        prompt: str,
    ) -> str:
        """
        Trim the prompt to the configured maximum size.

        Prefer trimming at the last newline so we avoid
        cutting a line in half whenever possible.
        """

        limit = self.config.max_prompt_characters

        if len(prompt) <= limit:
            return prompt

        trimmed = prompt[:limit]

        last_newline = trimmed.rfind("\n")

        if last_newline > 0:
            return trimmed[:last_newline]

        return trimmed


prompt_optimizer = PromptOptimizer()