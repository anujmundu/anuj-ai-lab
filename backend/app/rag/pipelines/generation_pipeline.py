from dataclasses import dataclass

from app.rag.performance_profiler import (
    PerformanceProfiler,
)

from app.rag.enums import (
    PerformanceStageName,
)

from app.services.ollama_service import (
    ollama_service,
)


@dataclass(slots=True)
class GenerationPipelineResult:

    raw_answer: str

    generation_seconds: float
    
class GenerationPipeline:

    def run(
        self,
        *,
        prompt: str,
        profiler: PerformanceProfiler | None = None,
        api_key: str | None = None,
        provider: str | None = None,
    ) -> GenerationPipelineResult:

        if profiler:

            with profiler.measure(
                PerformanceStageName.LLM_GENERATION,
            ):

                return self._generate(
                    prompt,
                    api_key=api_key,
                    provider=provider,
                )

        return self._generate(
            prompt,
            api_key=api_key,
            provider=provider,
        )
        
    def _generate(
        self,
        prompt: str,
        api_key: str | None = None,
        provider: str | None = None,
    ) -> GenerationPipelineResult:

        raw_answer = ollama_service.generate(
            prompt=prompt,
            api_key=api_key,
            provider=provider,
        )

        generation_seconds = (
            ollama_service.last_generation.get(
                "latency_seconds",
                0.0,
             )
        )

        return GenerationPipelineResult(
            raw_answer=raw_answer,
            generation_seconds=generation_seconds,
        )

generation_pipeline = GenerationPipeline()