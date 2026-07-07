export interface Memory {
    id: number;
    content: string;
    category: string;
    importance: number;
    pinned: boolean;
    created_at: string;
    updated_at: string;
}

export interface CreateMemoryRequest {
    content: string;
    category: string;
    importance: number;
}

export interface UpdateMemoryRequest {
    content: string;
    category: string;
    importance: number;
    pinned: boolean;
}