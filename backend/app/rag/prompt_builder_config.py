from dataclasses import dataclass


@dataclass(slots=True)
class PromptBuilderConfig:
    """
    Configuration for PromptBuilder.

    Controls how prompts are assembled before
    being sent to the language model.
    """

    # --------------------------------------------------
    # Grounding
    # --------------------------------------------------

    strict_grounding: bool = True

    preserve_terminology: bool = True

    unknown_answer: str = (
        "I don't have enough information "
        "in the retrieved documents."
    )

    # --------------------------------------------------
    # Answer Generation
    # --------------------------------------------------

    max_answer_sentences: int = 5

    # --------------------------------------------------
    # Prompt Sections
    # --------------------------------------------------

    include_conversation: bool = False

    include_citations: bool = False