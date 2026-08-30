import { api } from "@/lib/api";

export interface AgentMessage {
    id?: string;
    sender_role: "orchestrator" | "researcher" | "coder" | "critic" | "summarizer";
    recipient_role?: string;
    content: string;
    message_type?: string;
    timestamp: number;
}

export interface CollaborationSession {
    session_id: string;
    goal: string;
    status: "initializing" | "in_progress" | "awaiting_approval" | "completed" | "failed";
    participants?: string[];
    messages: AgentMessage[];
    blackboard?: any[];
    final_synthesis?: string | null;
    pending_approval?: {
        action_name: string;
        details: any;
    } | null;
    created_at: number;
    updated_at?: number;
}

export const collaborationService = {
    async createSession(goal: string): Promise<{ session_id: string; goal: string; status: string }> {
        const { data } = await api.post("/collaboration/sessions", { goal });
        return data;
    },

    async getSession(sessionId: string): Promise<CollaborationSession> {
        const { data } = await api.get<CollaborationSession>(`/collaboration/sessions/${sessionId}`);
        return data;
    },

    async listSessions(): Promise<CollaborationSession[]> {
        const { data } = await api.get<CollaborationSession[]>("/collaboration/sessions");
        return data;
    },

    async approveAction(sessionId: string, approved: boolean): Promise<any> {
        const { data } = await api.post(`/collaboration/sessions/${sessionId}/approve`, { approved });
        return data;
    },
};
