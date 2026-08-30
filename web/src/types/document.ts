export interface IngestResponse {
    filename?: string;
    status?: string;
    chunks_indexed?: number;
    chunk_ids?: string[];
    asset_id?: string;
    job_id?: string;
    job_status?: string;
    original_filename?: string;
    size_bytes?: number;
    progress?: number;
    error?: string;
}

export interface DocumentInfo {
    filename: string;
    chunks: number;
}