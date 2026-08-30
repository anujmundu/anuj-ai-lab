import { api } from "@/lib/api";

export interface ChatSessionSummary {
    session_id: string;
    title: string;
    summary?: string | null;
    created_at: string;
    updated_at: string;
}

export interface StoredChatMessage {
    id?: number;
    role: "user" | "assistant";
    content: string;
    sources?: any[];
    created_at: string;
}

export interface ChatSessionDetails {
    session_id: string;
    title: string;
    summary?: string | null;
    created_at: string;
    updated_at: string;
    messages: StoredChatMessage[];
}

export const chatSessionService = {
    async listSessions(): Promise<ChatSessionSummary[]> {
        const { data } = await api.get<ChatSessionSummary[]>("/chat/sessions");
        return data;
    },

    async createSession(title = "New Conversation"): Promise<ChatSessionSummary> {
        const { data } = await api.post<ChatSessionSummary>("/chat/sessions", { title });
        return data;
    },

    async getSession(sessionId: string): Promise<ChatSessionDetails> {
        const { data } = await api.get<ChatSessionDetails>(`/chat/sessions/${sessionId}`);
        return data;
    },

    async deleteSession(sessionId: string): Promise<void> {
        await api.delete(`/chat/sessions/${sessionId}`);
    },

    async renameSession(sessionId: string, title: string): Promise<ChatSessionSummary> {
        const { data } = await api.patch<ChatSessionSummary>(`/chat/sessions/${sessionId}`, { title });
        return data;
    },

    async sendMessage(sessionId: string, content: string): Promise<{ answer: string; sources: any[]; session_title?: string; confidence?: number }> {
        const apiKey = localStorage.getItem("anuj_ai_cloud_api_key") || undefined;
        const provider = localStorage.getItem("anuj_ai_cloud_provider") || undefined;
        const { data } = await api.post(`/chat/sessions/${sessionId}/messages`, {
            content,
            api_key: apiKey,
            provider: provider,
        });
        return data;
    },
};
