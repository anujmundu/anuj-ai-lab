import { api } from "@/lib/api";

import type { HealthResponse } from "@/types";

export const healthService = {
    async getHealth(): Promise<HealthResponse> {
        const { data } =
            await api.get<HealthResponse>("/");

        return data;
    },
};