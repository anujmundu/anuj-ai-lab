import { api } from "@/lib/api";

export interface ToolParameter {
    name: string;
    type: string;
    description: string;
    required: boolean;
}

export interface ToolDefinition {
    name: string;
    description: string;
    parameters?: Record<string, any>;
    category?: "native" | "mcp" | "multimodal";
}

export interface ToolExecutionResult {
    tool_name: string;
    success: boolean;
    output: any;
    error?: string | null;
    execution_time_ms?: number;
}

export const toolsService = {
    async getMcpTools(): Promise<ToolDefinition[]> {
        try {
            const { data } = await api.get("/mcp/tools");
            return Array.isArray(data) ? data : data.tools || [];
        } catch {
            return [];
        }
    },

    async getMcpServers(): Promise<any[]> {
        try {
            const { data } = await api.get("/mcp/servers");
            return Array.isArray(data) ? data : data.servers || [];
        } catch {
            return [];
        }
    },

    async executeMcpTool(toolName: string, args: Record<string, any>): Promise<ToolExecutionResult> {
        const { data } = await api.post<ToolExecutionResult>("/mcp/tools/call", {
            name: toolName,
            arguments: args,
        });
        return data;
    },

    async getToolsCatalog(): Promise<any[]> {
        try {
            const { data } = await api.get("/tools/catalog");
            return data.tools || [];
        } catch {
            return [];
        }
    },

    async executeTool(toolName: string, parameters: Record<string, any>): Promise<ToolExecutionResult> {
        const { data } = await api.post<ToolExecutionResult>("/tools/execute", {
            tool_name: toolName,
            parameters,
        });
        return data;
    },
};
