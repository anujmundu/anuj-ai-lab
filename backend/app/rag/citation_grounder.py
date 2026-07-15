import re

from app.rag.citation_grounder_config import (
    CitationGrounderConfig,
)
from app.rag.semantic_matcher import (
    semantic_matcher,
)


class CitationGrounder:
    """
    Semantic citation grounding engine.

    Responsibilities

    • Sentence segmentation
    • Sentence-to-source semantic matching
    • Multi-source grounding
    • Grounding confidence estimation
    • Grounding diagnostics

    This module performs no retrieval.

    It only evaluates how well retrieved
    documents support generated sentences.
    """

    def __init__(
        self,
        config: CitationGrounderConfig | None = None,
    ):

        self.config = (
            config
            or CitationGrounderConfig()
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _split_sentences(
        self,
        answer: str,
    ) -> list[str]:

        sentences = re.split(
            self.config.sentence_split_pattern,
            answer.strip(),
        )

        cleaned = []

        for sentence in sentences:

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

            if (
                len(sentence)
                < self.config.minimum_sentence_length
            ):
                continue

            cleaned.append(
                sentence,
            )

        return cleaned

    # --------------------------------------------------

    def _confidence_label(
        self,
        score: float,
    ) -> str:

        if score >= self.config.high_confidence:
            return "High"

        if score >= self.config.medium_confidence:
            return "Medium"

        if score >= self.config.low_confidence:
            return "Low"

        return "Very Low"

    # --------------------------------------------------

    def _grounding_status(
        self,
        score: float,
    ) -> str:

        if (
            score
            >= self.config.grounded_threshold
        ):
            return "grounded"

        if (
            score
            >= self.config.partial_grounding_threshold
        ):
            return "partially_grounded"

        return "unsupported"

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def ground(
        self,
        *,
        answer: str,
        documents: list[str],
        sources: list[dict],
    ) -> dict:

        if not self.config.enabled:

            return {}

        sentences = self._split_sentences(
            answer,
        )

        sentence_results = []

        grounded = 0
        partial = 0
        unsupported = 0

        confidence_sum = 0.0

        for sentence in sentences:

            matches = []

            for document, source in zip(
                documents,
                sources,
            ):

                similarity = (
                    semantic_matcher.compare(
                        sentence,
                        document,
                    )
                )

                score = (
                    similarity
                    .get(
                        "metrics",
                        {},
                    )
                    .get(
                        "overall",
                        0.0,
                    )
                )

                if (
                    score
                    < self.config.minimum_similarity
                ):
                    continue

                matches.append(
                    {
                        "similarity": score,

                        "metrics": similarity.get(
                            "metrics",
                            {},
                        ),

                        "confidence": similarity.get(
                            "confidence",
                            {},
                        ),

                        "diagnostics": similarity.get(
                            "diagnostics",
                            {},
                        ),

                        "explanation": similarity.get(
                            "explanation",
                            [],
                        ),

                        "source": source,
                    }
                )

            matches.sort(
                key=lambda item:
                item["similarity"],
                reverse=True,
            )

            matches = matches[
                :
                self.config.maximum_sources_per_sentence
            ]

            if matches:

                confidence = (
                    sum(
                        item["similarity"]
                        for item in matches
                    )
                    / len(matches)
                )

            else:

                confidence = 0.0

            status = (
                self._grounding_status(
                    confidence,
                )
            )

            if status == "grounded":

                grounded += 1

            elif status == "partially_grounded":

                partial += 1

            else:

                unsupported += 1

            confidence_sum += confidence

            sentence_results.append(
                {

                    "sentence": sentence,

                    "status": status,

                    "confidence": round(
                        confidence,
                        3,
                    ),

                    "confidence_label": (
                        self._confidence_label(
                            confidence,
                        )
                    ),

                    "matches": [
                        {

                            "filename":
                                match["source"]["filename"],

                            "chunk_id":
                                match["source"]["chunk_id"],

                            "chunk_number":
                                match["source"]["chunk_number"],

                            "similarity":
                                round(
                                    match["similarity"],
                                    3,
                                ),

                            "metrics":
                                (
                                    match["metrics"]
                                    if self.config.include_similarity_breakdown
                                    else {}
                                ),

                            "confidence":
                                (
                                    match["confidence"]
                                    if self.config.enable_confidence_scoring
                                    else {}
                                ),

                            "diagnostics":
                                match["diagnostics"],

                            "explanation":
                                match["explanation"],
                        }
                        for match in matches
                    ],
                }
            )

        total = len(
            sentence_results,
        )

        average_confidence = (
            confidence_sum
            / total
            if total
            else 0.0
        )
        
        grounding_score = (
            (
                grounded
                + (0.5 * partial)
            )
            / total
            if total
            else 0.0
        )

        return {

            "grounded_sentences":
                grounded,

            "partially_grounded_sentences":
                partial,

            "unsupported_sentences":
                unsupported,

            "grounding_score":
                round(
                    grounding_score,
                    3,
                ),

            "average_confidence":
                round(
                    average_confidence,
                    3,
                ),

            "overall_status":
                self._confidence_label(
                    average_confidence,
                ),

            "sentence_grounding":
                sentence_results,
        }


citation_grounder = (
    CitationGrounder()
)