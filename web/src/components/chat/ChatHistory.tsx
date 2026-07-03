import type { ChatMessage } from "@/types";

import { ChatMessage as MessageCard } from "./ChatMessage";

interface ChatHistoryProps {
    messages: ChatMessage[];
}

export function ChatHistory({
    messages,
}: ChatHistoryProps) {
    return (
        <div className="flex flex-col gap-4">
            {messages.map((message, index) => (
                <MessageCard
                    key={index}
                    role={message.role}
                    content={message.content}
                    sources={message.sources}
                />
            ))}
        </div>
    );
}