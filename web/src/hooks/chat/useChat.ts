import { useState } from "react";

import { useAsk } from "@/hooks/rag/useAsk";
import { useChatStore } from "@/stores";

export function useChat() {
    const [question, setQuestion] = useState("");

    const messages = useChatStore(
        (state) => state.messages,
    );

    const addMessage = useChatStore(
        (state) => state.addMessage,
    );

    const askMutation = useAsk();

    function sendMessage() {
        const trimmed = question.trim();

        if (
            !trimmed ||
            askMutation.isPending
        ) {
            return;
        }

        addMessage({
            role: "user",
            content: trimmed,
        });

        setQuestion("");

        askMutation.mutate(
            {
                question: trimmed,
                conversation: null,
            },
            {
                onSuccess(response) {
                    addMessage({
                        role: "assistant",
                        content: response.answer,
                        sources: response.sources,
                    });
                },

                onError(error) {
                    addMessage({
                        role: "assistant",
                        content:
                            error.message ??
                            "An unexpected error occurred.",
                    });
                },
            },
        );
    }

    return {
        question,
        setQuestion,
        sendMessage,
        messages,
        isPending: askMutation.isPending,
    };
}