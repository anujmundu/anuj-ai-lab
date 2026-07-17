from pydantic import BaseModel, Field


class SemanticRerankerConfig(BaseModel):
    """
    Configuration for the semantic reranking stage.

    Responsibilities
    ----------------
    • Enable/disable reranking
    • Configure score fusion weights
    • Control reranking diagnostics
    """

    enable_reranking: bool = Field(
        default=True,
        description="Enable semantic reranking after vector retrieval.",
    )

    chroma_weight: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Weight assigned to the original Chroma similarity.",
    )

    semantic_weight: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Weight assigned to SemanticMatcher similarity.",
    )

    include_diagnostics: bool = Field(
        default=True,
        description="Include reranking diagnostics in the response.",
    )
    
    candidate_multiplier: int = Field(
        default=5,
        ge=1,
        description="Number of retrieval candidates per requested document.",
    )

    minimum_candidates: int = Field(
        default=20,
        ge=1,
        description="Minimum number of semantic candidates retrieved before reranking.",
    )

    maximum_candidates: int = Field(
        default=100,
        ge=1,
        description="Upper bound on semantic retrieval candidates.",
    )