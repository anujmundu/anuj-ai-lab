import { ChatMessage } from "./ChatMessage";

export interface Message {
    role: "user" | "assistant";
    content: string;
}

interface ChatHistoryProps {
    messages: Message[];
}

export function ChatHistory({
    messages,
}: ChatHistoryProps) {
    return (
        <div className="space-y-4">
            {messages.map((message, index) => (
                <ChatMessage
                    key={index}
                    role={message.role}
                    content={message.content}
                />
            ))}
        </div>
    );
}