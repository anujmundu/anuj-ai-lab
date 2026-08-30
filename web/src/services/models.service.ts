import { api } from "@/lib/api";

export interface AvailableModelsResponse {
    installed_models: string[];
    preferred_tiers?: Record<string, string | string[]>;
    tier_mapping?: Record<string, string | string[]>;
    fallback_model?: string;
}

export interface SetPrimaryTierResponse {
    status: string;
    task_type: string;
    primary_model: string;
    tier_models: string[];
    preferred_tiers: Record<string, string[]>;
}

export interface ModelRouteResponse {
    task_type: string;
    recommended_model: string;
    reason: string;
}

export const modelsService = {
    async getAvailableModels(): Promise<AvailableModelsResponse> {
        const { data } = await api.get<AvailableModelsResponse>("/models/available");
        return data;
    },

    async setPrimaryModel(taskType: string, modelName: string): Promise<SetPrimaryTierResponse> {
        const { data } = await api.post<SetPrimaryTierResponse>("/models/tiers/primary", {
            task_type: taskType,
            model_name: modelName,
        });
        return data;
    },

    async routeTask(query: string, userOverride?: string): Promise<ModelRouteResponse> {
        const { data } = await api.post<ModelRouteResponse>("/models/route", {
            query,
            user_override_model: userOverride,
        });
        return data;
    },
};
