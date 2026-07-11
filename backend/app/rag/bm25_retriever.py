import math
import re
from collections import Counter, defaultdict


class BM25Retriever:
    """
    BM25 keyword retriever.

    Responsibilities

    • Build a lightweight BM25 index
    • Rank documents using keyword matching
    • Return document indices with scores

    Future responsibilities

    • Persistent indexing
    • Incremental updates
    • Synonym expansion
    • Field weighting
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.k1 = k1
        self.b = b

        self.documents: list[str] = []
        self.document_tokens: list[list[str]] = []

        self.document_lengths: list[int] = []

        self.average_document_length = 0.0

        self.term_frequencies: list[Counter] = []

        self.document_frequencies = defaultdict(int)

        self.idf: dict[str, float] = {}

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _tokenize(
        self,
        text: str,
    ) -> list[str]:

        return re.findall(
            r"\b\w+\b",
            text.lower(),
        )

    # --------------------------------------------------
    # Index
    # --------------------------------------------------

    def build(
        self,
        documents: list[str],
    ) -> None:

        self.documents = documents

        self.document_tokens = []

        self.term_frequencies = []

        self.document_lengths = []

        self.document_frequencies.clear()

        self.idf.clear()

        for document in documents:

            tokens = self._tokenize(
                document,
            )

            self.document_tokens.append(
                tokens,
            )

            frequencies = Counter(
                tokens,
            )

            self.term_frequencies.append(
                frequencies,
            )

            self.document_lengths.append(
                len(tokens),
            )

            for token in frequencies.keys():
                self.document_frequencies[token] += 1

        if documents:

            self.average_document_length = (
                sum(self.document_lengths)
                / len(documents)
            )

        total_documents = len(documents)

        for token, frequency in (
            self.document_frequencies.items()
        ):

            self.idf[token] = math.log(
                (
                    total_documents
                    - frequency
                    + 0.5
                )
                /
                (
                    frequency
                    + 0.5
                )
                + 1
            )

    # --------------------------------------------------
    # Search
    # --------------------------------------------------

    def search(
        self,
        query: str,
        k: int = 5,
    ) -> list[tuple[int, float]]:

        if not self.documents:
            return []

        query_tokens = self._tokenize(
            query,
        )

        scores = []

        for index in range(
            len(self.documents)
        ):

            score = 0.0

            frequencies = (
                self.term_frequencies[index]
            )

            document_length = (
                self.document_lengths[index]
            )

            for token in query_tokens:

                if token not in frequencies:
                    continue

                frequency = frequencies[token]

                idf = self.idf.get(
                    token,
                    0.0,
                )

                numerator = (
                    frequency
                    * (self.k1 + 1)
                )

                denominator = (
                    frequency
                    + self.k1
                    * (
                        1
                        - self.b
                        + self.b
                        * (
                            document_length
                            / self.average_document_length
                        )
                    )
                )

                score += (
                    idf
                    * numerator
                    / denominator
                )

            scores.append(
                (
                    index,
                    score,
                )
            )

        scores.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        return scores[:k]


bm25_retriever = BM25Retriever()