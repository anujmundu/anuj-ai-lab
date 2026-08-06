from dataclasses import dataclass

from app.rag.pipeline_health import pipeline_health
from app.rag.rag_scorecard import rag_scorecard


@dataclass(slots=True)
class EvaluationPipelineResult:

    pipeline_health: dict

    scorecard: dict


class EvaluationPipeline:
    """
    Evaluate the quality of the completed RAG pipeline.

    Responsibilities

    • Pipeline health
    • Scorecard generation
    """

    def run(
        self,
        *,
        retrieval_quality: dict,
        prompt_quality: dict,
        answer_quality: dict,
        hallucination: dict,
        citations: dict,
    ) -> EvaluationPipelineResult:

        pipeline_health_result = (
            pipeline_health.evaluate(
                retrieval_quality=retrieval_quality,
                hallucination=hallucination,
                answer_quality=answer_quality,
                citation_result=citations,
            )
        )

        scorecard_result = (
            rag_scorecard.build(
                retrieval_quality=retrieval_quality,
                prompt_quality=prompt_quality,
                answer_quality=answer_quality,
                hallucination=hallucination,
                citations=citations,
            )
        )

        return EvaluationPipelineResult(
            pipeline_health=pipeline_health_result,
            scorecard=scorecard_result,
        )


evaluation_pipeline = EvaluationPipeline()