import { api } from "@/lib/api";

import type {
    DocumentInfo,
    IngestResponse,
} from "@/types/document";

export const documentService = {
    async getDocuments(): Promise<DocumentInfo[]> {
        try {
            const { data } = await api.get<DocumentInfo[]>("/documents");
            if (Array.isArray(data)) {
                localStorage.setItem("anuj_ai_documents", JSON.stringify(data));
                return data;
            }
        } catch {
            // Fallback to local storage cache if network fails
        }
        try {
            const cached = localStorage.getItem("anuj_ai_documents");
            return cached ? JSON.parse(cached) : [];
        } catch {
            return [];
        }
    },

    async ingest(file: File): Promise<IngestResponse> {
        const formData = new FormData();
        formData.append("file", file);

        const { data } = await api.post<IngestResponse>("/ingest", formData, {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        });

        // Optimistically update document cache
        try {
            const cached: DocumentInfo[] = JSON.parse(localStorage.getItem("anuj_ai_documents") || "[]");
            const newDoc: DocumentInfo = {
                filename: file.name,
                chunks: data.chunks_indexed || 1,
            };
            const updated = [newDoc, ...cached.filter((d) => d.filename !== file.name)];
            localStorage.setItem("anuj_ai_documents", JSON.stringify(updated));
        } catch {
            // ignore
        }

        return data;
    },

    async deleteDocument(filename: string): Promise<void> {
        try {
            await api.delete(`/documents/${filename}`);
        } catch {
            // ignore
        }
        try {
            const cached: DocumentInfo[] = JSON.parse(localStorage.getItem("anuj_ai_documents") || "[]");
            const updated = cached.filter((d) => d.filename !== filename);
            localStorage.setItem("anuj_ai_documents", JSON.stringify(updated));
        } catch {
            // ignore
        }
    },
};