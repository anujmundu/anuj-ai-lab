import type { AskResponse } from "./rag";

export type ChatSource = AskResponse["sources"][number];

export interface ChatMessage {
    role: "user" | "assistant";
    content: string;
    sources?: ChatSource[];
}

export interface ChatConversation {
    id: string;

    title?: string;

    createdAt?: string;

    updatedAt?: string;

    messages: ChatMessage[];
}