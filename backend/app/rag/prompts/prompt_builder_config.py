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
        "I don't have enough information to answer that based on the available memory and retrieved context."
    )

    # --------------------------------------------------
    # Answer Generation
    # --------------------------------------------------

    max_answer_sentences: int = 5

    # --------------------------------------------------
    # Prompt Sections
    # --------------------------------------------------

    include_conversation: bool = True

    include_citations: bool = False