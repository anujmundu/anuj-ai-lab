from dataclasses import dataclass


@dataclass(slots=True)
class HallucinationClaimExtractorConfig:
    """
    Configuration for claim extraction.

    This component extracts factual claims from
    generated answers before hallucination
    analysis.

    It performs no semantic verification.
    """

    # --------------------------------------------------
    # Master Switches
    # --------------------------------------------------

    enabled: bool = True

    normalize_claims: bool = True

    remove_duplicate_claims: bool = True

    include_tokenization: bool = True

    # --------------------------------------------------
    # Sentence Processing
    # --------------------------------------------------

    sentence_split_pattern: str = (
        r"(?<=[.!?])\s+"
    )

    minimum_claim_length: int = 20

    ignore_non_text_sentences: bool = True

    # --------------------------------------------------
    # Claim Filtering
    # --------------------------------------------------

    remove_inline_citations: bool = True

    remove_trailing_whitespace: bool = True

    lowercase_normalization: bool = False

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------

    include_statistics: bool = True

    include_normalized_claim: bool = True

    include_tokens: bool = True