interface ChatMessageProps {
    role: "user" | "assistant";
    content: string;
}

export function ChatMessage({
    role,
    content,
}: ChatMessageProps) {
    return (
        <div className="rounded-lg border p-3">
            <div className="mb-2 text-xs font-semibold uppercase text-muted-foreground">
                {role}
            </div>

            <p className="whitespace-pre-wrap text-sm">
                {content}
            </p>
        </div>
    );
}