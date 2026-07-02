export interface AskRequest {
    question: string;
    conversation?: string | null;
}

export interface SourceInfo {
    filename: string;
    chunk_id: string;
    chunk_number: number;
    total_chunks: number;
}

export interface AskResponse {
    question: string;
    answer: string;
    confidence: number;
    sources: SourceInfo[];
}