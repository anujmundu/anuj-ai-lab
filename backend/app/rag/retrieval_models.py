from dataclasses import dataclass


@dataclass(slots=True)
class RetrievalMetadata:
    """
    Canonical metadata describing a retrieved document chunk.
    """

    filename: str = ""

    chunk_id: str = ""

    chunk_number: int = 0

    total_chunks: int = 0

    source: str = ""


@dataclass(slots=True)
class RetrievalScores:
    """
    Canonical retrieval scores produced throughout the
    retrieval pipeline.
    """

    semantic_score: float = 0.0

    keyword_score: float = 0.0

    combined_score: float = 0.0


@dataclass(slots=True)
class RetrievalResult:
    """
    Canonical representation of a retrieved chunk.

    This object is independent of any retrieval backend
    and becomes the standard retrieval model used
    throughout the RAG pipeline.
    """

    doc_id: str

    document: str

    metadata: RetrievalMetadata

    scores: RetrievalScores

    @property
    def filename(self) -> str:
        return self.metadata.filename

    @property
    def chunk_id(self) -> str:
        return self.metadata.chunk_id or self.doc_id

    @property
    def chunk_number(self) -> int:
        return self.metadata.chunk_number

    @property
    def total_chunks(self) -> int:
        return self.metadata.total_chunks

    @property
    def source(self) -> str:
        return self.metadata.source

    @property
    def semantic_score(self) -> float:
        return self.scores.semantic_score

    @property
    def keyword_score(self) -> float:
        return self.scores.keyword_score

    @property
    def combined_score(self) -> float:
        return self.scores.combined_score