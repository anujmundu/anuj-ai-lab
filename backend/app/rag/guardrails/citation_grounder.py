from ctypes import alignment

from app.rag.citation_grounder_config import (
    CitationGrounderConfig,
)
from app.rag.evidence_models import (
    EvidenceAlignmentResult,
    EvidenceMatch,
)


class CitationGrounder:
    """
    Transforms an EvidenceAlignmentResult into a
    citation grounding report.

    This class performs no retrieval,
    sentence segmentation,
    semantic matching,
    or evidence alignment.

    All evidence computation is delegated
    to EvidenceAligner.
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
    
    def _serialize_primary_match(
        self,
        match: EvidenceMatch,
    ) -> dict:
        """
        Convert the strongest supporting evidence into a
        lightweight summary.
        """

        return {

            "filename":
                match.filename,

            "chunk_id":
                match.chunk_id,

            "chunk_number":
                match.chunk_number,

            "similarity":
                round(
                    match.score.overall,
                    3,
                ),

            "support":
                match.support.value,
        }
    
    def _serialize_match(
        self,
        match: EvidenceMatch,
    ) -> dict:
        """
        Serialize one evidence match.
        """

        return {

            "filename":
                match.filename,

            "chunk_id":
                match.chunk_id,

            "chunk_number":
                match.chunk_number,

            "similarity":
                round(
                    match.score.overall,
                    3,
                ),

            "metrics":
                {

                    "overall":
                        round(
                            match.score.overall,
                            3,
                        ),

                    "lexical":
                        round(
                            match.score.lexical,
                            3,
                        ),

                    "embedding":
                        round(
                            match.score.embedding,
                            3,
                        ),
                },

            "confidence":
                {

                    "score":
                        round(
                            match.score.overall,
                            3,
                        ),

                    "label":
                        self._confidence_label(
                            match.score.overall,
                        ),
                },

            "support":
                match.support.value,
        }

    # --------------------------------------------------

    def _confidence_label(
        self,
        score: float,
    ) -> str:
        """
        Convert a confidence score into a human-readable label.
        """

        score = max(
            0.0,
            min(score, 1.0),
        )

        if score >= self.config.high_confidence:
            return "High"

        if score >= self.config.medium_confidence:
            return "Medium"

        if score >= self.config.low_confidence:
            return "Low"

        return "Very Low"

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def ground(
        self,
        *,
        alignment: EvidenceAlignmentResult,
    ) -> dict:
        
        

        if not self.config.enabled:
            return {}

        sentence_results = []

        for sentence in alignment.sentences:

            sentence_results.append(
                {

                    "sentence":
                        sentence.sentence,

                    "status":
                        sentence.support.value,

                    "confidence":
                        round(
                            sentence.confidence,
                            3,
                        ),

                    "confidence_label":
                        self._confidence_label(
                            sentence.confidence,
                        ),

                    "primary_match":
                        (
                            self._serialize_primary_match(
                                sentence.best_match,
                            )
                            if sentence.best_match
                            else None
                        ),

                    "matches":
                        [
                            self._serialize_match(match)
                            for match in sentence.candidate_matches
                        ],
                }
            )

        return {

            "grounded_sentences":
                alignment.grounded_count,

            "partially_grounded_sentences":
                alignment.partial_count,

            "unsupported_sentences":
                alignment.unsupported_count,

            "grounding_score":
                alignment.grounding_score,

            "average_confidence":
                round(
                    alignment.average_confidence,
                    3,
                ),

            "overall_status":
                self._confidence_label(
                    alignment.average_confidence,
                ),

            "sentence_grounding":
                sentence_results,
        }


citation_grounder = (
    CitationGrounder()
)