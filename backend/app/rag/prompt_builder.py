from app.rag.prompt_builder_config import PromptBuilderConfig


class PromptBuilder:
    """
    Builds prompts for the language model.

    Responsibilities

    • Build structured prompts
    • Enforce grounding rules
    • Support future conversation memory
    • Keep prompting independent from retrieval

    Future responsibilities

    • Few-shot examples
    • Dynamic system prompts
    • Citation instructions
    • Prompt compression
    """

    def __init__(
        self,
        config: PromptBuilderConfig | None = None
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
            "Answer the user's question using ONLY "
            "the retrieved context."
        )

    def _rules_section(self) -> str:

        rules: list[str] = []

        if self.config.strict_grounding:

            rules.extend([
                "- Use ONLY the retrieved context.",
                "- Never invent facts.",
                "- Never use outside knowledge."
            ])

        if self.config.preserve_terminology:

            rules.append(
                "- Preserve technical terminology exactly as written."
            )

        rules.extend([
            "- Keep the answer concise and accurate.",
            (
                "- Limit the answer to approximately "
                f"{self.config.max_answer_sentences} sentences."
            ),
            (
                "- If the answer cannot be found in the "
                "retrieved context, reply exactly:"
            ),
            f'  "{self.config.unknown_answer}"'
        ])

        return (
            "RULES\n"
            "-----\n"
            + "\n".join(rules)
        )

    def _conversation_section(
        self,
        conversation: str | None
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

    def _context_section(
        self,
        context: str
    ) -> str:

        return (
            "CONTEXT\n"
            "-------\n"
            f"{context}"
        )

    def _question_section(
        self,
        question: str
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

    def _build_sections(
        self,
        question: str,
        context: str,
        conversation: str | None
    ) -> list[str]:
        """
        Assemble all prompt sections.

        Keeping this separate ensures build_prompt()
        remains a very small public method as new
        sections (citations, memory, examples, tool
        outputs, etc.) are added in future commits.
        """

        return [
            self._role_section(),
            self._task_section(),
            self._rules_section(),
            self._conversation_section(
                conversation
            ),
            self._context_section(
                context
            ),
            self._question_section(
                question
            ),
            self._answer_section()
        ]

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def build_prompt(
        self,
        question: str,
        context: str,
        conversation: str | None = None
    ) -> str:
        """
        Build the final prompt.

        Parameters
        ----------
        question
            User question.

        context
            Structured context produced by ContextBuilder.

        conversation
            Reserved for future conversation memory.
        """

        sections = self._build_sections(
            question=question,
            context=context,
            conversation=conversation
        )

        return "\n\n".join(sections).strip()


prompt_builder = PromptBuilder()