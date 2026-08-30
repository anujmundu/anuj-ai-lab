import re

from app.rag.prompt_normalizer_config import PromptNormalizerConfig
from app.rag.prompt_optimizer_models import PromptComponent


class PromptNormalizer:
    """
    Performs lightweight normalization of prompt components
    before analysis and optimization.

    Responsibilities
    ----------------
    - Remove empty components
    - Trim leading/trailing whitespace
    - Normalize blank lines
    - Collapse repeated spaces

    Does NOT:
    - Render prompts
    - Allocate token budgets
    - Remove important content
    """

    def __init__(
        self,
        config: PromptNormalizerConfig | None = None,
    ):
        self.config = config or PromptNormalizerConfig()

    def normalize(
        self,
        components: list[PromptComponent],
    ) -> list[PromptComponent]:

        if not self.config.enable_optimization:
            return components

        normalized_components: list[PromptComponent] = []

        for component in components:

            text = component.text.strip()

            if self.config.remove_trailing_whitespace:
                text = self._remove_trailing_whitespace(text)

            if self.config.normalize_blank_lines:
                text = self._normalize_blank_lines(text)

            if self.config.collapse_multiple_spaces:
                text = self._collapse_multiple_spaces(text)

            if not text:
                continue

            normalized_components.append(
                PromptComponent(
                    component_type=component.component_type,
                    text=text,
                    tokens=component.tokens,
                    characters=len(text),
                    priority=component.priority,
                    required=component.required,
                )
            )

        return normalized_components

    @staticmethod
    def _remove_trailing_whitespace(
        prompt: str,
    ) -> str:

        return "\n".join(
            line.rstrip()
            for line in prompt.splitlines()
        )

    @staticmethod
    def _normalize_blank_lines(
        prompt: str,
    ) -> str:

        return re.sub(
            r"\n{3,}",
            "\n\n",
            prompt,
        )

    @staticmethod
    def _collapse_multiple_spaces(
        prompt: str,
    ) -> str:

        return re.sub(
            r"[ ]{2,}",
            " ",
            prompt,
        )


prompt_normalizer = PromptNormalizer()