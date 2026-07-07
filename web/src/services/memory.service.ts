import { api } from "@/lib/api";

import type {
    CreateMemoryRequest,
    Memory,
    UpdateMemoryRequest,
} from "@/types/memory";

export const memoryService = {
    async getAll(): Promise<Memory[]> {
        const { data } = await api.get<Memory[]>(
            "/memory",
        );

        return data;
    },

    async search(
        query: string,
    ): Promise<Memory[]> {
        const { data } = await api.get<Memory[]>(
            "/memory/search",
            {
                params: {
                    query,
                },
            },
        );

        return data;
    },

    async create(
        memory: CreateMemoryRequest,
    ): Promise<Memory> {
        const { data } = await api.post<Memory>(
            "/memory",
            memory,
        );

        return data;
    },

    async update(
        id: number,
        memory: UpdateMemoryRequest,
    ): Promise<Memory> {
        const { data } = await api.put<Memory>(
            `/memory/${id}`,
            memory,
        );

        return data;
    },

    async delete(
        id: number,
    ): Promise<void> {
        await api.delete(
            `/memory/${id}`,
        );
    },
};