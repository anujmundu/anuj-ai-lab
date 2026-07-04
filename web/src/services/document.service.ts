import { api } from "@/lib/api";

import type {
    DocumentInfo,
    IngestResponse,
} from "@/types/document";

export const documentService = {
    async getDocuments(): Promise<DocumentInfo[]> {
        const { data } =
            await api.get<DocumentInfo[]>(
                "/documents",
            );

        return data;
    },

    async ingest(
        file: File,
    ): Promise<IngestResponse> {
        const formData =
            new FormData();

        formData.append(
            "file",
            file,
        );

        const { data } =
            await api.post<IngestResponse>(
                "/ingest",
                formData,
                {
                    headers: {
                        "Content-Type":
                            "multipart/form-data",
                    },
                },
            );

        return data;
    },

    async deleteDocument(
        filename: string,
    ): Promise<void> {
        await api.delete(
            `/documents/${filename}`,
        );
    },
};