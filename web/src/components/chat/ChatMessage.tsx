import type { ChatSource } from "@/types";
import { useUIStore } from "@/stores";
import { FileText, Sparkles } from "lucide-react";

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
    const toggleInspector = useUIStore((state) => state.toggleInspector);
    const inspectorOpen = useUIStore((state) => state.inspectorOpen);

    const isLlmRequiredPrompt = content.includes("Neural LLM Engine Required");

    return (
        <div
            className={`rounded-xl border p-4 transition-colors ${
                role === "assistant"
                    ? "bg-card border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white"
                    : "bg-slate-100 dark:bg-slate-900/60 border-slate-200 dark:border-slate-800 text-slate-800 dark:text-slate-200"
            }`}
        >
            <div className="mb-2 flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                <span>{role === "assistant" ? "🤖 AI Assistant" : "👤 You"}</span>
                {role === "assistant" && sources && sources.length > 0 && (
                    <button
                        onClick={toggleInspector}
                        className="flex items-center gap-1 text-[11px] text-indigo-600 dark:text-indigo-400 hover:underline font-normal cursor-pointer normal-case"
                        title={inspectorOpen ? "View in open Execution Inspector" : "Open Execution Inspector"}
                    >
                        <FileText className="h-3 w-3" />
                        <span>{sources.length} {sources.length === 1 ? "source" : "sources"} in Inspector</span>
                    </button>
                )}
            </div>

            <div className="whitespace-pre-wrap leading-7 text-sm">
                {content}
            </div>

            {isLlmRequiredPrompt && (
                <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-800">
                    <button
                        onClick={() => window.dispatchEvent(new CustomEvent("open-llm-key-modal"))}
                        className="px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-medium text-xs flex items-center gap-2 shadow-md hover:shadow-lg transition-all cursor-pointer"
                    >
                        <Sparkles className="h-4 w-4" /> ⚡ Connect Free Cloud LLM (Groq / Gemini)
                    </button>
                </div>
            )}
        </div>
    );
}