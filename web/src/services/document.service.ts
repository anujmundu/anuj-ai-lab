import { api } from "@/lib/api";

import type {
    DocumentInfo,
    IngestResponse,
} from "@/types/document";

export const documentService = {
    async getDocuments(): Promise<DocumentInfo[]> {
        const response = await api.get<DocumentInfo[]>(
            "/documents",
        );

        console.log(
            "[documentService] GET /documents",
            response.data,
        );

        return response.data;
    },

    async ingest(
        file: File,
    ): Promise<IngestResponse> {
        const formData = new FormData();

        formData.append(
            "file",
            file,
        );

        const response = await api.post<IngestResponse>(
            "/ingest",
            formData,
            {
                headers: {
                    "Content-Type":
                        "multipart/form-data",
                },
            },
        );

        return response.data;
    },

    async deleteDocument(
        filename: string,
    ): Promise<void> {
        await api.delete(
            `/documents/${filename}`,
        );
    },
};