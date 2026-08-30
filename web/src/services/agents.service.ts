import { api } from "@/lib/api";

export interface AgentSubTask {
    id: string;
    description: string;
    tool_name?: string | null;
    dependencies?: string[];
    status?: string;
    result?: any;
}

export interface AgentPlan {
    goal: string;
    subtasks: AgentSubTask[];
}

export interface AgentStep {
    step_number: number;
    thought: string;
    action: string;
    action_input?: any;
    observation?: any;
    reflection?: string;
    success?: boolean;
    execution_time_ms?: number;
}

export interface AgentTask {
    task_id: string;
    goal: string;
    status: "pending" | "planning" | "running" | "reflecting" | "completed" | "failed" | "cancelled";
    plan?: AgentPlan | null;
    steps: AgentStep[];
    result?: string | null;
    error?: string | null;
    created_at: number;
    updated_at?: number;
}

export const agentsService = {
    async createTask(goal: string, maxSteps = 8): Promise<{ task_id: string; goal: string; status: string }> {
        const { data } = await api.post("/agents/tasks", {
            goal,
            max_steps: maxSteps,
        });
        return data;
    },

    async getTask(taskId: string): Promise<AgentTask> {
        const { data } = await api.get<AgentTask>(`/agents/tasks/${taskId}`);
        return data;
    },

    async listTasks(): Promise<AgentTask[]> {
        const { data } = await api.get<AgentTask[]>("/agents/tasks");
        return data;
    },
};
