import re

from .models import QueryAnalysis


QUESTION_WORDS = {
    "what",
    "why",
    "when",
    "where",
    "who",
    "which",
    "how",
}

BOOLEAN_OPERATORS = {
    "and",
    "or",
    "not",
}

TEMPORAL_WORDS = {
    "today",
    "yesterday",
    "tomorrow",
    "before",
    "after",
    "during",
    "current",
    "latest",
    "recent",
}

COMPARISON_WORDS = {
    "compare",
    "difference",
    "better",
    "versus",
    "vs",
}


class QueryAnalyzer:

    def analyze(
        self,
        query: str,
    ) -> QueryAnalysis:

        words = re.findall(r"\w+", query.lower())

        token_count = len(words)

        return QueryAnalysis(
            token_count=token_count,
            character_count=len(query),
            word_count=token_count,
            contains_question_word=any(
                word in QUESTION_WORDS
                for word in words
            ),
            contains_number=any(
                word.isdigit()
                for word in words
            ),
            contains_boolean_operator=any(
                word in BOOLEAN_OPERATORS
                for word in words
            ),
            contains_temporal_reference=any(
                word in TEMPORAL_WORDS
                for word in words
            ),
            contains_comparison=any(
                word in COMPARISON_WORDS
                for word in words
            ),
            estimated_complexity=(
                "complex"
                if token_count > 12
                else "simple"
            ),
        )


query_analyzer = QueryAnalyzer()