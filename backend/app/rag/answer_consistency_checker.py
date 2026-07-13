import re

from app.rag.answer_consistency_checker_config import (
    AnswerConsistencyCheckerConfig,
)


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "by",
    "for",
    "from",
    "have",
    "has",
    "had",
    "i",
    "in",
    "including",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "there",
    "they",
    "this",
    "to",
    "was",
    "were",
    "with",
    "you",
    "your",
}


class AnswerConsistencyChecker:
    """
    Estimates internal consistency of generated answers.

    Responsibilities

    • Normalize text
    • Split answer into sentences
    • Compare sentence pairs
    • Estimate consistency
    • Produce diagnostics only

    Future responsibilities

    • NLI verification
    • Entity consistency
    • Numerical consistency
    • Temporal consistency
    • LLM self verification
    """

    def __init__(
        self,
        config: AnswerConsistencyCheckerConfig | None = None,
    ):

        self.config = (
            config
            or AnswerConsistencyCheckerConfig()
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _normalize(
        self,
        text: str,
    ) -> str:

        if self.config.ignore_case:
            text = text.lower()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    def _tokenize(
        self,
        text: str,
    ) -> set[str]:

        text = self._normalize(text)

        tokens = set(
            re.findall(
                r"\b\w+\b",
                text,
            )
        )

        return {
            token
            for token in tokens
            if (
                len(token)
                >= self.config.minimum_token_length
                and token not in STOPWORDS
            )
        }

    def _sentence_similarity(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> float:

        tokens_a = self._tokenize(
            sentence_a
        )

        tokens_b = self._tokenize(
            sentence_b
        )

        if (
            not tokens_a
            or not tokens_b
        ):
            return 0.0

        overlap = (
            tokens_a
            & tokens_b
        )

        union = (
            tokens_a
            | tokens_b
        )

        return (
            len(overlap)
            / len(union)
        )

    def _compare_sentences(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> dict | None:

        similarity = self._sentence_similarity(
            sentence_a,
            sentence_b,
        )

        if (
            similarity
            >= self.config.minimum_overlap
        ):
            return None

        return {
            "sentence_a": sentence_a,
            "sentence_b": sentence_b,
            "similarity": round(
                similarity,
                2,
            ),
            "reason": "Low semantic overlap",
        }

    def _analyze_pairs(
        self,
        sentences: list[str],
    ) -> tuple[list[dict], int]:

        issues = []

        pair_count = 0

        for i in range(len(sentences)):

            for j in range(i + 1, len(sentences)):

                pair_count += 1

                issue = self._compare_sentences(
                    sentences[i],
                    sentences[j],
                )

                if issue is not None:

                    issues.append(issue)

        return (
            issues,
            pair_count,
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def detect(
        self,
        answer: str,
    ) -> dict:

        if not self.config.enabled:

            return {
                "status": "disabled",
                "consistent": True,
                "total_sentences": 0,
                "sentence_pairs": 0,
                "possible_conflicts": 0,
                "consistency_score": None,
                "details": [],
            }

        sentences = re.split(
            self.config.sentence_split_regex,
            answer.strip(),
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        # Ignore citation-only fragments
        sentences = [
            sentence
            for sentence in sentences
            if not re.fullmatch(
                r"(?:\[\d+\]\s*)+",
                sentence,
            )
        ]

        issues, pair_count = (
            self._analyze_pairs(
                sentences
            )
        )

        if pair_count == 0:

            score = 1.0

        else:

            score = (
                1
                - (
                    len(issues)
                    / pair_count
                )
            )

        score = round(
            score,
            2,
        )

        if score >= self.config.contradiction_threshold:

            status = "consistent"

        elif score >= 0.50:

            status = "uncertain"

        else:

            status = "needs_review"

        return {

            "status": status,

            "consistent": (
                status == "consistent"
            ),

            "total_sentences": len(
                sentences
            ),

            "sentence_pairs": pair_count,

            "possible_conflicts": len(
                issues
            ),

            "consistency_score": score,

            "details": issues,
        }


answer_consistency_checker = (
    AnswerConsistencyChecker()
)