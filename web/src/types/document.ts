export interface IngestResponse {
    filename: string;
    status: string;
    chunks_indexed: number;
    chunk_ids: string[];
}

export interface DocumentInfo {
    filename: string;
    chunks: number;
}