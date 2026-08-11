from __future__ import annotations

import re

from app.rag.query.enums import (
    QueryAmbiguity,
    QueryComplexity,
    QueryIntent,
)
from app.rag.query.models import QueryAnalysisResult


class QueryAnalyzer:
    """
    Deterministic query analyzer.

    Responsibilities:
    - Detect query intent
    - Estimate query complexity
    - Estimate ambiguity
    - Determine whether rewriting may help
    - Determine whether multi-query retrieval may help

    This layer performs no LLM calls.
    """

    DEFINITION_WORDS = {
        "what",
        "define",
        "definition",
        "meaning",
        "means",
    }

    EXPLANATION_WORDS = {
        "why",
        "explain",
        "explanation",
        "reason",
    }

    PROCEDURE_WORDS = {
        "steps",
        "step",
        "procedure",
        "process",
        "implement",
        "implementation",
        "build",
        "create",
        "configure",
        "setup",
        "set",
    }

    COMPARISON_WORDS = {
        "compare",
        "comparison",
        "difference",
        "differences",
        "versus",
        "vs",
        "better",
        "worse",
        "similar",
        "different",
    }

    RESEARCH_WORDS = {
        "research",
        "comprehensive",
        "survey",
        "literature",
        "investigate",
        "investigation",
        "analysis",
        "analyze",
        "review",
        "study",
        "evaluate",
        "evaluation",
    }

    FACTUAL_WORDS = {
        "who",
        "when",
        "where",
        "which",
        "date",
        "year",
        "number",
    }

    AMBIGUOUS_WORDS = {
        "it",
        "this",
        "that",
        "they",
        "them",
        "thing",
        "stuff",
        "one",
        "some",
        "something",
    }

    MULTI_QUERY_WORDS = {
        "compare",
        "comparison",
        "difference",
        "differences",
        "versus",
        "vs",
        "research",
        "comprehensive",
        "survey",
        "literature",
        "multiple",
    }

    def analyze(
        self,
        query: str,
    ) -> QueryAnalysisResult:
        """
        Analyze a user query deterministically.
        """

        normalized_query = query.strip().lower()

        words = re.findall(
            r"\b[\w'-]+\b",
            normalized_query,
        )

        if not normalized_query:
            return QueryAnalysisResult(
                query=query,
                intent=QueryIntent.UNKNOWN,
                complexity=QueryComplexity.SIMPLE,
                ambiguity=QueryAmbiguity.HIGH,
                requires_rewrite=True,
                requires_multi_query=False,
            )

        intent = self._detect_intent(
            normalized_query,
            words,
        )

        complexity = self._detect_complexity(
            normalized_query,
            words,
            intent,
        )

        ambiguity = self._detect_ambiguity(
            normalized_query,
            words,
        )

        requires_rewrite = (
            ambiguity == QueryAmbiguity.HIGH
            or complexity == QueryComplexity.COMPLEX
        )

        requires_multi_query = (
            intent in {
                QueryIntent.COMPARISON,
                QueryIntent.RESEARCH,
            }
            or any(
                word in self.MULTI_QUERY_WORDS
                for word in words
            )
        )

        return QueryAnalysisResult(
            query=query,
            intent=intent,
            complexity=complexity,
            ambiguity=ambiguity,
            requires_rewrite=requires_rewrite,
            requires_multi_query=requires_multi_query,
        )

    def _detect_intent(
        self,
        query: str,
        words: list[str],
    ) -> QueryIntent:
        """
        Determine the dominant query intent.
        """

        word_set = set(words)

        # Comparison gets priority.
        if (
            word_set & self.COMPARISON_WORDS
            or "versus" in query
            or " vs " in f" {query} "
        ):
            return QueryIntent.COMPARISON

        # Research / survey-style queries.
        if word_set & self.RESEARCH_WORDS:
            return QueryIntent.RESEARCH

        # Definition queries.
        if (
            "what is" in query
            or "what are" in query
            or "define" in query
            or "definition" in query
            or "meaning" in query
        ):
            return QueryIntent.DEFINITION

        # Procedure queries.
        if (
            "how to" in query
            or "steps to" in query
            or word_set & self.PROCEDURE_WORDS
        ):
            return QueryIntent.PROCEDURE

        # Explanation queries.
        if (
            word_set & self.EXPLANATION_WORDS
            or "how does" in query
            or "how do" in query
            or "why does" in query
            or "why do" in query
        ):
            return QueryIntent.EXPLANATION

        # Factual queries.
        if (
            word_set & self.FACTUAL_WORDS
            or "how many" in query
            or "how much" in query
        ):
            return QueryIntent.FACTUAL

        return QueryIntent.UNKNOWN

    def _detect_complexity(
        self,
        query: str,
        words: list[str],
        intent: QueryIntent,
    ) -> QueryComplexity:
        """
        Estimate query complexity using deterministic signals.
        """

        word_count = len(words)

        complexity_score = 0

        if word_count > 20:
            complexity_score += 3
        elif word_count > 12:
            complexity_score += 2
        elif word_count > 6:
            complexity_score += 1

        complexity_score += query.count(",")
        complexity_score += query.count(";")

        logical_words = {
            "and",
            "or",
            "but",
            "while",
            "although",
        }

        complexity_score += sum(
            1
            for word in words
            if word in logical_words
        )

        if intent == QueryIntent.COMPARISON:
            complexity_score += 1

        if intent == QueryIntent.RESEARCH:
            complexity_score += 2

        if complexity_score >= 4:
            return QueryComplexity.COMPLEX

        if complexity_score >= 2:
            return QueryComplexity.MEDIUM

        return QueryComplexity.SIMPLE

    def _detect_ambiguity(
        self,
        query: str,
        words: list[str],
    ) -> QueryAmbiguity:
        """
        Estimate whether the query lacks sufficient context.
        """

        if not words:
            return QueryAmbiguity.HIGH

        ambiguity_score = 0

        if len(words) <= 2:
            ambiguity_score += 2
        elif len(words) <= 4:
            ambiguity_score += 1

        ambiguity_score += sum(
            1
            for word in words
            if word in self.AMBIGUOUS_WORDS
        )

        generic_patterns = {
            "explain this",
            "tell me about this",
            "what about this",
            "how does it work",
            "what is it",
        }

        if query in generic_patterns:
            ambiguity_score += 3

        if ambiguity_score >= 3:
            return QueryAmbiguity.HIGH

        if ambiguity_score >= 1:
            return QueryAmbiguity.MEDIUM

        return QueryAmbiguity.LOW


query_analyzer = QueryAnalyzer()