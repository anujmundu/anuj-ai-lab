import { useForm } from "react-hook-form";
import { Sparkles, Brain } from "lucide-react";
import { useCreateMemory } from "@/hooks";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

type FormData = {
    content: string;
    category: string;
    importance: number;
};

const CATEGORIES = [
    { value: "general", label: "General Context" },
    { value: "architecture", label: "System Architecture" },
    { value: "user_preference", label: "User & Developer Preference" },
    { value: "technical_spec", label: "Technical Specification" },
    { value: "project_rules", label: "Project Rules & Guidelines" },
    { value: "meeting_notes", label: "Meeting Notes & Decisions" },
    { value: "security_policy", label: "Security & Guardrails" },
];

export default function MemoryForm() {
    const createMemory = useCreateMemory();

    const {
        register,
        handleSubmit,
        reset,
    } = useForm<FormData>({
        defaultValues: {
            content: "",
            category: "general",
            importance: 3,
        },
    });

    async function onSubmit(values: FormData) {
        await createMemory.mutateAsync(values);
        reset();
    }

    return (
        <Card className="p-5 border border-slate-200 dark:border-slate-800 shadow-sm bg-white dark:bg-slate-900">
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="flex items-center gap-2 text-sm font-semibold text-slate-900 dark:text-white">
                    <Brain className="h-4 w-4 text-indigo-500" />
                    <span>Store New Semantic Memory Fact</span>
                </div>

                <Input
                    placeholder="Enter memory fact (e.g. 'Always prioritize using local Ollama model fleet instead of external APIs')..."
                    className="text-xs"
                    {...register("content", { required: true })}
                />

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {/* Category Dropdown */}
                    <div>
                        <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                            Memory Category:
                        </label>
                        <select
                            {...register("category")}
                            className="w-full text-xs bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg p-2.5 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                        >
                            {CATEGORIES.map((c) => (
                                <option key={c.value} value={c.value}>
                                    {c.label}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Importance Level */}
                    <div>
                        <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                            Importance Rating:
                        </label>
                        <select
                            {...register("importance", { valueAsNumber: true })}
                            className="w-full text-xs bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg p-2.5 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                        >
                            <option value={1}>1 - Low Priority</option>
                            <option value={2}>2 - Standard Context</option>
                            <option value={3}>3 - Medium Importance</option>
                            <option value={4}>4 - High Priority</option>
                            <option value={5}>5 - Critical Core Knowledge</option>
                        </select>
                    </div>
                </div>

                <Button
                    type="submit"
                    disabled={createMemory.isPending}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white text-xs gap-1.5"
                >
                    <Sparkles className="h-3.5 w-3.5" />
                    {createMemory.isPending ? "Saving Fact..." : "Save Memory Fact"}
                </Button>
            </form>
        </Card>
    );
}