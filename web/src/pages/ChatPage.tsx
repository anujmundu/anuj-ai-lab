import { useState } from "react";

import {
    ChatHistory,
    ChatInput,
    type Message,
} from "@/components/chat";

import { useAsk } from "@/hooks";

export default function ChatPage() {
    const ask = useAsk();

    const [question, setQuestion] = useState("");

    const [messages, setMessages] = useState<Message[]>([]);

    const handleSubmit = () => {
        if (!question.trim()) {
            return;
        }

        const userQuestion = question;

        setMessages((previous) => [
            ...previous,
            {
                role: "user",
                content: userQuestion,
            },
        ]);

        setQuestion("");

        ask.mutate(
            {
                question: userQuestion,
                conversation: null,
            },
            {
                onSuccess(response) {
                    setMessages((previous) => [
                        ...previous,
                        {
                            role: "assistant",
                            content: response.answer,
                        },
                    ]);
                },
            },
        );
    };

    return (
        <section className="flex flex-1 flex-col gap-6 p-6">
            <div>
                <h1 className="text-2xl font-bold">
                    AI Assistant
                </h1>

                <p className="text-muted-foreground">
                    Ask questions using the Retrieval-Augmented Generation pipeline
                </p>
            </div>

            <ChatHistory
                messages={messages}
            />

            <ChatInput
                value={question}
                onChange={setQuestion}
                onSubmit={handleSubmit}
                disabled={ask.isPending}
            />
        </section>
    );
}