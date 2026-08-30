from pydantic import BaseModel, Field


class EvidenceAlignerConfig(BaseModel):
    """
    Configuration for the EvidenceAligner.
    """

    grounded_threshold: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
    )

    partial_threshold: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
    )

    minimum_similarity: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
    )

    max_candidate_matches: int = Field(
        default=3,
        ge=1,
    )

    store_all_matches: bool = False

    sort_descending: bool = True

    #
    # Evidence scoring weights
    #

    lexical_weight: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
    )

    embedding_weight: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
    )


#
# Singleton configuration
#

evidence_config = EvidenceAlignerConfig()