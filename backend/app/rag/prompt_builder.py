from app.rag.prompt_builder_config import PromptBuilderConfig

from app.rag.prompt_optimizer_models import PromptComponent
from app.rag.enums import PromptComponentType


class PromptBuilder:
    """
    Builds prompts for the language model.

    Responsibilities

    • Build structured prompts
    • Enforce grounding rules
    • Support conversation history
    • Support persistent memory
    • Keep prompting independent from retrieval

    Future responsibilities

    • Few-shot examples
    • Dynamic system prompts
    • Citation instructions
    • Prompt compression
    """

    def __init__(
        self,
        config: PromptBuilderConfig | None = None,
    ):
        self.config = config or PromptBuilderConfig()

    # --------------------------------------------------
    # Sections
    # --------------------------------------------------

    def _role_section(self) -> str:
        return (
            "ROLE\n"
            "----\n"
            "You are a helpful AI assistant."
        )

    def _task_section(self) -> str:
        return (
            "TASK\n"
            "----\n"
            "Answer the user's question using ONLY the "
            "MEMORY section and the retrieved CONTEXT section."
        )

    def _rules_section(self) -> str:
        rules: list[str] = []

        if self.config.strict_grounding:
            rules.extend(
                [
                    "- Use ONLY the MEMORY section and the retrieved CONTEXT section.",
                    "- Never invent facts.",
                    "- Never use outside knowledge.",
                ]
            )

        if self.config.preserve_terminology:
            rules.append(
                "- Preserve technical terminology exactly as written."
            )

        rules.extend(
            [
                "- Keep the answer concise and accurate.",
                (
                    "- Limit the answer to approximately "
                    f"{self.config.max_answer_sentences} sentences."
                ),
                (
                    "- If the answer cannot be found in the "
                    "MEMORY section or the retrieved CONTEXT section, "
                    "reply exactly:"
                ),
                f'  "{self.config.unknown_answer}"',
            ]
        )

        return (
            "RULES\n"
            "-----\n"
            + "\n".join(rules)
        )

    def _conversation_section(
        self,
        conversation: str | None,
    ) -> str:

        if not self.config.include_conversation:
            conversation = "(none)"

        elif not conversation:
            conversation = "(none)"

        return (
            "CONVERSATION\n"
            "------------\n"
            f"{conversation}"
        )

    def _memory_section(
        self,
        memory: str | None,
    ) -> str:
        """
        Persistent long-term memory.

        This section is intentionally separate from
        retrieved documents and conversation history.
        """

        if not memory:
            memory = "(none)"

        return (
            "MEMORY\n"
            "------\n"
            "These are persistent facts about the user. "
            "Treat them as true when answering questions.\n\n"
            f"{memory}"
        )

    def _context_section(
        self,
        context: str,
    ) -> str:
        return (
            "CONTEXT\n"
            "-------\n"
            f"{context}"
        )

    def _question_section(
        self,
        question: str,
    ) -> str:
        return (
            "QUESTION\n"
            "--------\n"
            f"{question}"
        )

    def _answer_section(self) -> str:
        return (
            "ANSWER\n"
            "------"
        )

    # --------------------------------------------------
    # Prompt Assembly
    # --------------------------------------------------

    def _build_components(
        self,
        *,
        question: str,
        context: str,
        conversation: str | None,
        memory: str | None,
    ) -> list[PromptComponent]:
        """
        Assemble prompt components.

        Each logical section of the prompt becomes a
        PromptComponent that can later be analyzed,
        optimized, budgeted and rendered.
        """

        components = [
            PromptComponent(
                component_type=PromptComponentType.SYSTEM,
                text=self._role_section(),
                priority=0,
                required=True,
            ),
            PromptComponent(
                component_type=PromptComponentType.SYSTEM,
                text=self._task_section(),
                priority=1,
                required=True,
            ),
            PromptComponent(
                component_type=PromptComponentType.SYSTEM,
                text=self._rules_section(),
                priority=2,
                required=True,
            ),
            PromptComponent(
                component_type=PromptComponentType.CONVERSATION,
                text=self._conversation_section(
                    conversation,
                ),
                priority=3,
                required=False,
            ),
            PromptComponent(
                component_type=PromptComponentType.MEMORY,
                text=self._memory_section(
                    memory,
                ),
                priority=4,
                required=False,
            ),
            PromptComponent(
                component_type=PromptComponentType.CONTEXT,
                text=self._context_section(
                    context,
                ),
                priority=5,
                required=True,
            ),
            PromptComponent(
                component_type=PromptComponentType.QUESTION,
                text=self._question_section(
                    question,
                ),
                priority=6,
                required=True,
            ),
            PromptComponent(
                component_type=PromptComponentType.SYSTEM,
                text=self._answer_section(),
                priority=7,
                required=True,
            ),
        ]

        return components

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def build_prompt(
        self,
        *,
        question: str,
        context: str,
        conversation: str | None = None,
        memory: str | None = None,
    ) -> list[PromptComponent]:
        """
        Build structured prompt components.

        Rendering into the final prompt string is
        handled by PromptRenderer.
        """

        return self._build_components(
            question=question,
            context=context,
            conversation=conversation,
            memory=memory,
        )


prompt_builder = PromptBuilder()