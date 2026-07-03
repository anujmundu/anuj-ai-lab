import { create } from "zustand";

import type { ChatMessage } from "@/types";

interface ChatState {
    messages: ChatMessage[];

    addMessage: (
        message: ChatMessage,
    ) => void;

    replaceLastMessage: (
        message: ChatMessage,
    ) => void;

    removeLastMessage: () => void;

    clearMessages: () => void;
}

export const useChatStore =
    create<ChatState>((set) => ({
        messages: [],

        addMessage: (
            message,
        ) =>
            set((state) => ({
                messages: [
                    ...state.messages,
                    message,
                ],
            })),

        replaceLastMessage: (
            message,
        ) =>
            set((state) => ({
                messages: [
                    ...state.messages.slice(
                        0,
                        -1,
                    ),
                    message,
                ],
            })),

        removeLastMessage: () =>
            set((state) => ({
                messages:
                    state.messages.slice(
                        0,
                        -1,
                    ),
            })),

        clearMessages: () =>
            set({
                messages: [],
            }),
    }));