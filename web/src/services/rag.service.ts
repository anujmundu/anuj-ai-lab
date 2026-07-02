import { api } from "../lib/api";

import type {
    AskRequest,
    AskResponse,
} from "../types/rag";


export const ragService = {

    async ask(
        request: AskRequest,
    ): Promise<AskResponse> {

        const { data } = await api.post<AskResponse>(
            "/rag/ask",
            request,
        );

        return data;

    },

    async search(
        query: string,
        k = 3,
    ) {

        const { data } = await api.get(
            "/rag/search",
            {
                params: {
                    query,
                    k,
                },
            },
        );

        return data;

    },

};