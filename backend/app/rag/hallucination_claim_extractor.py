import re

from app.rag.hallucination_claim_extractor_config import (
    HallucinationClaimExtractorConfig,
)


class HallucinationClaimExtractor:
    """
    Extracts factual claims from an answer.

    Responsibilities

    • Sentence segmentation
    • Claim normalization
    • Duplicate removal
    • Tokenization

    No hallucination scoring is performed here.
    """

    def __init__(
        self,
        config: HallucinationClaimExtractorConfig | None = None,
    ):

        self.config = (
            config
            or HallucinationClaimExtractorConfig()
        )

    # --------------------------------------------------

    def _normalize(
        self,
        claim: str,
    ) -> str:

        if self.config.remove_inline_citations:

            claim = re.sub(
                r"\[\d+\]",
                "",
                claim,
            )

        if self.config.remove_trailing_whitespace:

            claim = claim.strip()

        if self.config.lowercase_normalization:

            claim = claim.lower()

        return claim

    # --------------------------------------------------

    @staticmethod
    def _tokenize(
        text: str,
    ) -> list[str]:

        return re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )

    # --------------------------------------------------

    def extract(
        self,
        answer: str,
    ) -> dict:

        if not self.config.enabled:

            return {}

        sentences = re.split(
            self.config.sentence_split_pattern,
            answer.strip(),
        )

        claims = []

        seen = set()

        for index, sentence in enumerate(sentences, start=1,):

            sentence = sentence.strip()

            if not sentence:
                continue

            if (
                self.config.ignore_non_text_sentences
                and
                not re.search(
                    r"[A-Za-z]",
                    sentence,
                )
            ):
                continue

            normalized = self._normalize(
                sentence,
            )

            if (
                len(normalized)
                < self.config.minimum_claim_length
            ):
                continue

            if (
                self.config.remove_duplicate_claims
                and normalized in seen
            ):
                continue

            seen.add(
                normalized,
            )

            claim = {

                "index": index,

                "claim": sentence,

                "normalized": normalized,
            }

            if self.config.include_tokens:

                claim["tokens"] = (
                    self._tokenize(
                        normalized,
                    )
                )

            claims.append(
                claim,
            )

        result = {
            "index": index,

            "claims": claims,
        }

        if self.config.include_statistics:

            result["statistics"] = {

                "claim_count": len(
                    claims,
                ),

                "average_length": round(
                    (
                        sum(
                            len(
                                item["normalized"]
                            )
                            for item in claims
                        )
                        / len(claims)
                    )
                    if claims
                    else 0,
                    1,
                ),
            }

        return result


hallucination_claim_extractor = (
    HallucinationClaimExtractor()
)