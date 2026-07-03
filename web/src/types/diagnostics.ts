export interface Timings {
    retrieval_seconds: number;
    context_build_seconds: number;
    prompt_build_seconds: number;
    generation_seconds: number;
    total_seconds: number;
}

export interface PromptInfo {
    characters: number;
    words: number;
}

export interface ResponseInfo {
    characters: number;
    words: number;
}

export interface HallucinationInfo {
    hallucination_risk: number;
    context_overlap: number;
    supported_terms: number;
    unsupported_terms: number;
    unsupported_term_list: string[];
    is_potential_hallucination: boolean;
}

export interface SourceMapping {
    citation: string;
    filename: string;
    chunk_id: string;
    chunk_number: number;
    total_chunks: number;
}

export interface CitationInfo {
    answer: string;
    citations: string[];
    source_mapping: SourceMapping[];
}

export interface GenerationInfo {
    model: string;
    temperature: number;
    top_p: number;
    repeat_penalty: number;
    seed: number;
    max_tokens: number;
    stream: boolean;
    latency_seconds: number;
    prompt_characters: number;
    prompt_words: number;
    response_characters: number;
    response_words: number;
}

export interface DiagnosticsRequest {
    question: string;
    timings: Timings;
    prompt: PromptInfo;
    response: ResponseInfo;
    confidence: number;
    hallucination: HallucinationInfo;
    citations: CitationInfo;
}

export interface DiagnosticsResponse {
    request: DiagnosticsRequest;
    generation: GenerationInfo;
}