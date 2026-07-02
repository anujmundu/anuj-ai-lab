import { api } from "../lib/api";

import type {
    DiagnosticsResponse,
} from "../types/diagnostics";


export const diagnosticsService = {

    async getDiagnostics(): Promise<DiagnosticsResponse> {

        const { data } = await api.get<DiagnosticsResponse>(
            "/rag/diagnostics",
        );

        return data;

    },

};