from collections import defaultdict


class RankFusion:
    """
    Reciprocal Rank Fusion (RRF).

    Responsibilities

    • Fuse multiple ranked retrieval lists
    • Preserve rankings from different retrievers
    • Produce a single unified ranking

    Future responsibilities

    • Weighted RRF
    • Additional retrievers
    • Score normalization
    • Configurable fusion strategies
    """

    def __init__(
        self,
        rrf_k: int = 60,
    ):

        self.rrf_k = rrf_k

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def _rrf_score(
        self,
        rank: int,
    ) -> float:
        """
        Reciprocal Rank Fusion score.

        score = 1 / (k + rank)
        """

        return 1.0 / (
            self.rrf_k + rank
        )

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def fuse(
        self,
        *rankings: list[list[int]],
    ) -> list[int]:
        """
        Fuse multiple ranked document lists.

        Parameters
        ----------
        rankings

            [
                [3, 7, 1],
                [7, 5, 3]
            ]

        Returns
        -------
        [
            7,
            3,
            5,
            1
        ]
        """

        scores = defaultdict(float)

        for ranking in rankings:

            for rank, document_id in enumerate(
                ranking,
                start=1,
            ):

                scores[document_id] += (
                    self._rrf_score(rank)
                )

        fused = sorted(
            scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        return [
            document_id
            for document_id, _
            in fused
        ]


rank_fusion = RankFusion()