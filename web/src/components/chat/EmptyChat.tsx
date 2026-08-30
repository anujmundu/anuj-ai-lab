import { Sparkles, Bot, Key, BookOpen, Code, Lightbulb } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyChatProps {
    onConnectLLM?: () => void;
    onSelectPrompt?: (prompt: string) => void;
}

export function EmptyChat({ onConnectLLM, onSelectPrompt }: EmptyChatProps) {
    const isConnected = !!localStorage.getItem("anuj_ai_cloud_api_key");
    const provider = (localStorage.getItem("anuj_ai_cloud_provider") || "groq").toUpperCase();

    const samplePrompts = [
        { icon: Lightbulb, text: "Explain quantum entanglement to a 10-year-old" },
        { icon: BookOpen, text: "Tell me an epic story about Dune" },
        { icon: Code, text: "Write a Python script to scrape financial news and compute sentiment" },
        { icon: Bot, text: "What is the overall architecture of Anuj AI Lab?" },
    ];

    return (
        <div className="flex flex-1 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 p-6 sm:p-12 text-center max-w-2xl mx-auto space-y-6 my-auto">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-purple-500/10 text-purple-600 dark:text-purple-400 shadow-sm">
                <Sparkles className="h-7 w-7" />
            </div>

            <div className="space-y-2">
                <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                    Anuj AI Lab Intelligent Workspace
                </h2>
                <p className="text-xs sm:text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto">
                    {isConnected ? (
                        <span className="text-emerald-600 dark:text-emerald-400 font-medium">
                            ⚡ Connected to {provider === "GROQ" ? "Meta Llama 3.3 70B (Groq)" : provider}. Ready for boundless generation!
                        </span>
                    ) : (
                        "Multi-turn semantic conversations grounded in ChromaDB hybrid search & multi-agent deliberation."
                    )}
                </p>
            </div>

            {!isConnected && onConnectLLM && (
                <Button
                    onClick={onConnectLLM}
                    className="bg-purple-600 hover:bg-purple-700 text-white font-medium text-xs px-4 py-2 rounded-xl shadow-md flex items-center gap-2"
                >
                    <Key className="h-3.5 w-3.5" /> ⚡ Connect Free Cloud LLM (Groq / Gemini)
                </Button>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full pt-2">
                {samplePrompts.map((p, idx) => {
                    const Icon = p.icon;
                    return (
                        <button
                            key={idx}
                            onClick={() => onSelectPrompt?.(p.text)}
                            className="flex items-start gap-2.5 p-3 rounded-xl text-left text-xs bg-slate-50 dark:bg-slate-800/60 hover:bg-purple-50 dark:hover:bg-purple-950/30 border border-slate-200/60 dark:border-slate-800 text-slate-700 dark:text-slate-300 transition-all group"
                        >
                            <Icon className="h-4 w-4 text-purple-500 shrink-0 mt-0.5" />
                            <span className="line-clamp-2 group-hover:text-purple-600 dark:group-hover:text-purple-400">
                                {p.text}
                            </span>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}