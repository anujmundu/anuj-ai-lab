import { useState } from "react";

import {
    ChatHistory,
    ChatInput,
    EmptyChat,
    LoadingMessage,
} from "@/components/chat";

import { useAsk } from "@/hooks";

import type { ChatMessage } from "@/types";

export default function ChatPage() {
    const [question, setQuestion] = useState("");

    const [messages, setMessages] = useState<ChatMessage[]>([]);

    const askMutation = useAsk();

    function handleSubmit() {
        const trimmed = question.trim();

        if (!trimmed || askMutation.isPending) {
            return;
        }

        const userMessage: ChatMessage = {
            role: "user",
            content: trimmed,
        };

        setMessages((previous) => [
            ...previous,
            userMessage,
        ]);

        setQuestion("");

        askMutation.mutate(
            {
                question: trimmed,
                conversation: null,
            },
            {
                onSuccess(response) {
                    setMessages((previous) => [
                        ...previous,
                        {
                            role: "assistant",
                            content: response.answer,
                            sources: response.sources,
                        },
                    ]);
                },

                onError(error) {
                    setMessages((previous) => [
                        ...previous,
                        {
                            role: "assistant",
                            content:
                                error.message ??
                                "An unexpected error occurred.",
                        },
                    ]);
                },
            },
        );
    }

    return (
        <section className="flex flex-1 flex-col gap-6 p-6">
            <div>
                <h1 className="text-2xl font-bold">
                    AI Assistant
                </h1>

                <p className="text-muted-foreground">
                    Ask questions using the
                    Retrieval-Augmented Generation
                    pipeline.
                </p>
            </div>

            <div className="flex flex-1 flex-col gap-6">
                {messages.length === 0 ? (
                    <EmptyChat />
                ) : (
                    <ChatHistory
                        messages={messages}
                    />
                )}

                {askMutation.isPending && (
                    <LoadingMessage />
                )}
            </div>

            <ChatInput
                value={question}
                onChange={setQuestion}
                onSubmit={handleSubmit}
                disabled={askMutation.isPending}
            />
        </section>
    );
}