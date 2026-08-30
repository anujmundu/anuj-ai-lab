class PromptContract:
    """
    Defines the behavioral contract that every generated
    response must follow.

    The contract contains generation policies only.

    PromptBuilder is responsible for assembling prompt
    sections.

    PromptContract is responsible for defining how the
    language model should behave.
    """

    def build(
        self,
        *,
        strict_grounding: bool,
        preserve_terminology: bool,
        max_answer_sentences: int,
        unknown_answer: str,
    ) -> list[str]:

        rules: list[str] = []

        #
        # Strict evidence-grounded generation.
        #

        if strict_grounding:

            rules.extend(
                [
                    "- Use ONLY the supplied MEMORY and SOURCE sections.",
                    "- Treat every SOURCE block as factual evidence.",
                    "- Never use outside knowledge.",
                    "- Never rely on prior training knowledge.",
                    "- Never infer missing information.",
                    "- Never assume facts that are not explicitly stated.",
                    "- Do not generalize beyond the retrieved evidence.",
                    "- Do not combine unsupported ideas into new conclusions.",
                    "- Every factual sentence must be supported by one or more SOURCE blocks.",
                    "- If a statement is not supported by a SOURCE block, do not include it.",
                    "- When multiple SOURCE blocks support the same statement, prefer the strongest evidence.",
                    "- If the supplied evidence is insufficient, reply exactly with the unknown answer.",
                ]
            )

        #
        # Preserve wording.
        #

        if preserve_terminology:

            rules.extend(
                [
                    "- Preserve technical terminology exactly as it appears.",
                    "- Do not rename algorithms, models, datasets or frameworks.",
                ]
            )

        #
        # Citation policy.
        #

        rules.extend(
            [
                "- Cite supporting SOURCE identifiers whenever making factual statements.",
                "- Use the format [1], [2], [3].",
                "- Do not invent citation numbers.",
                "- Do not cite a SOURCE unless it supports the statement.",
            ]
        )

        #
        # Style.
        #

        rules.extend(
            [
                "- Keep the answer concise.",
                "- Avoid repetition.",
                f"- Limit the answer to approximately {max_answer_sentences} sentences.",
                f'- If the answer cannot be determined from MEMORY or SOURCE sections, reply exactly: "{unknown_answer}"',
            ]
        )

        return rules


prompt_contract = PromptContract()