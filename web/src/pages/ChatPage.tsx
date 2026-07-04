import {
    ChatHistory,
    ChatInput,
    EmptyChat,
    LoadingMessage,
} from "@/components/chat";

import { useChat } from "@/hooks";

export default function ChatPage() {
    const {
        question,
        setQuestion,
        sendMessage,
        messages,
        isPending,
    } = useChat();

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

                {isPending && (
                    <LoadingMessage />
                )}
            </div>

            <ChatInput
                value={question}
                onChange={setQuestion}
                onSubmit={sendMessage}
                disabled={isPending}
            />
        </section>
    );
}