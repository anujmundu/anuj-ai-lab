export interface DiagnosticsResponse {
    request: {
        question: string;

        timings: {
            retrieval_seconds: number;
            context_build_seconds: number;
            prompt_build_seconds: number;
            generation_seconds: number;
            total_seconds: number;
        };

        prompt: {
            characters: number;
            words: number;
        };

        response: {
            characters: number;
            words: number;
        };

        confidence: number;

        hallucination: Record<string, unknown>;

        citations: Record<string, unknown>;
    };

    generation: Record<string, unknown>;
}