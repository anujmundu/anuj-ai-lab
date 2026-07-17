import re

from app.rag.answer_consistency_checker_config import (
    AnswerConsistencyCheckerConfig,
)

from app.rag.embedding_similarity import (
    embedding_similarity,
)

from app.rag.contradiction_detector import (
    contradiction_detector,
)

from app.rag.nli_adapter import (
    nli_adapter,
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
        
    def _compare_sentences(
        self,
        sentence_a: str,
        sentence_b: str,
    ) -> dict:

        semantic = (
            embedding_similarity.compare(
                text_a=sentence_a,
                text_b=sentence_b,
            )
        )

        contradiction = (
            contradiction_detector.evaluate(
                claim=sentence_a,
                context=sentence_b,
                similarity=semantic,
            )
        )

        nli = (
            nli_adapter.infer(
                contradiction=contradiction,
            )
        )

        return {

            "sentence_a": sentence_a,

            "sentence_b": sentence_b,

            "semantic_similarity": semantic,

            "contradiction": contradiction,

            "nli": nli,
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

                comparison = self._compare_sentences(
                    sentences[i],
                    sentences[j],
                )

                issues.append(
                    comparison,
                )

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

        supported_pairs = 0

        neutral_pairs = 0

        contradicted_pairs = 0

        for pair in issues:

            label = pair["nli"]["label"]

            if label == "supported":

                supported_pairs += 1

            elif label in ("neutral", "unrelated"):

                neutral_pairs += 1

            elif label == "contradicted":

                contradicted_pairs += 1
                
        if pair_count:

            score = (

                supported_pairs

                + neutral_pairs

            ) / pair_count

        else:

            score = 1.0

        score = round(
            score,
            2,
        )

        if score >= self.config.consistent_threshold:

            status = "consistent"

        elif score >= self.config.uncertain_threshold:

            status = "uncertain"

        else:

            status = "needs_review"

        return {

            "status": status,

            "total_sentences": len(sentences),

            "sentence_pairs": pair_count,

            "supported_pairs": supported_pairs,

            "neutral_pairs": neutral_pairs,

            "contradicted_pairs": contradicted_pairs,

            "consistency_score": round(
                score,
                2,
            ),

            "details": issues,
        }


answer_consistency_checker = (
    AnswerConsistencyChecker()
)