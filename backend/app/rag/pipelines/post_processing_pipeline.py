from dataclasses import dataclass

from app.rag.answer_processor import (
    answer_processor,
)

from app.rag.answer_quality import (
    answer_quality,
)

from app.rag.citation_inserter import (
    citation_inserter,
)

from app.rag.citation_processor import (
    citation_processor,
)

from app.rag.evidence_aligner import (
    EvidenceAlignmentResult,
    evidence_aligner,
)

from app.rag.hallucination_detector import (
    hallucination_detector,
)

from app.rag.answer_consistency_checker import (
    answer_consistency_checker,
)

from app.rag.performance_profiler import (
    PerformanceProfiler,
)

from app.rag.enums import (
    PerformanceStageName,
)

@dataclass(slots=True)
class PostProcessingPipelineResult:

    answer: str

    confidence: float

    alignment: EvidenceAlignmentResult

    hallucination: dict

    consistency: dict

    answer_quality: dict

    citation_result: dict
    
class PostProcessingPipeline:

    def run(
        self,
        *,
        raw_answer: str,
        context: str,
        sources: list[dict],
        documents: list[str],
        metadatas: list[dict],
        profiler: PerformanceProfiler | None = None,
    ) -> PostProcessingPipelineResult:

        if profiler:

            with profiler.measure(
                PerformanceStageName.POST_PROCESSING,
            ):

                return self._process(
                    raw_answer=raw_answer,
                    context=context,
                    sources=sources,
                    documents=documents,
                    metadatas=metadatas,
                )

        return self._process(
            raw_answer=raw_answer,
            context=context,
            sources=sources,
            documents=documents,
            metadatas=metadatas,
        )
        
    def _process(
        self,
        *,
        raw_answer: str,
        context: str,
        sources: list[dict],
        documents: list[str],
        metadatas: list[dict],
    ) -> PostProcessingPipelineResult:
        processed_answer = (
            answer_processor.process(
                answer=raw_answer,
                    context=context,
                )
            )
        
        alignment = (
            evidence_aligner.align(
                answer=processed_answer["answer"],
                    documents=documents,
                    metadatas=metadatas,
                )
            )
        
        citation_insert_result = (
            citation_inserter.insert(
                    answer=processed_answer["answer"],
                    sources=sources,
                )
            )
        
        hallucination_result = (
            hallucination_detector.detect(
                    answer=citation_insert_result["answer"],
                    context=context,
                )
            )
        
        consistency_result = (
            answer_consistency_checker.detect(
                    answer=citation_insert_result["answer"],
                )
            )
        
        citation_result = (
            citation_processor.process(
                    answer=citation_insert_result["answer"],
                    sources=sources,
                    alignment=alignment,
                )
            )
        
        answer = citation_result["answer"]
        
        answer_quality_result = (
            answer_quality.analyze(
                    answer=answer,
                    prompt=context,
                )
            )
        
        confidence = processed_answer["confidence"]
        
        return PostProcessingPipelineResult(
            answer=answer,
            confidence=confidence,
            alignment=alignment,
            hallucination=hallucination_result,
            consistency=consistency_result,
            answer_quality=answer_quality_result,
            citation_result=citation_result,
        )

post_processing_pipeline = PostProcessingPipeline()