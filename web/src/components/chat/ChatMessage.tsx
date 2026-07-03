import type { ChatSource } from "@/types";

import { SourceList } from "./SourceList";

interface ChatMessageProps {
    role: "user" | "assistant";
    content: string;
    sources?: ChatSource[];
}

export function ChatMessage({
    role,
    content,
    sources,
}: ChatMessageProps) {
    return (
        <div
            className={`rounded-xl border p-4 ${
                role === "assistant"
                    ? "bg-card"
                    : "bg-muted"
            }`}
        >
            <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                {role}
            </div>

            <p className="whitespace-pre-wrap leading-7">
                {content}
            </p>

            {role === "assistant" &&
                sources &&
                sources.length > 0 && (
                    <div className="mt-5">
                        <SourceList
                            sources={sources}
                        />
                    </div>
                )}
        </div>
    );
}