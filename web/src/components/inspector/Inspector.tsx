import {
    Activity,
    AlertTriangle,
    Clock3,
    Database,
    FileText,
    ShieldCheck,
    Cpu,
    CheckCircle2,
    X,
} from "lucide-react";

import { useDiagnostics } from "@/hooks/rag/useDiagnostics";
import { useHealth } from "@/hooks/system/useHealth";
import { useUIStore } from "@/stores";

import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

export function Inspector() {
    const { data: diagnostics } = useDiagnostics();
    const { data: healthData } = useHealth();
    const selectedModel = useUIStore((state) => state.selectedModel);
    const toggleInspector = useUIStore((state) => state.toggleInspector);

    if (!diagnostics || !diagnostics.request || !diagnostics.request.question) {
        return (
            <aside className="h-full w-80 shrink-0 border-l border-slate-200 bg-white flex flex-col dark:border-slate-800 dark:bg-slate-950">
                <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3.5 dark:border-slate-800">
                    <div className="flex items-center gap-2">
                        <Activity className="h-4 w-4 text-emerald-500" />
                        <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            Telemetry Inspector
                        </h2>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={toggleInspector}
                        className="h-6 w-6 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                        title="Close Inspector"
                    >
                        <X className="h-3.5 w-3.5" />
                    </Button>
                </div>

                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {/* Live System Standby Card */}
                    <Card className="border border-slate-200 dark:border-slate-800 shadow-sm">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-xs uppercase tracking-wider text-slate-400 flex items-center justify-between">
                                <span>System Pulse</span>
                                <Badge variant="secondary" className="text-[10px] bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                                    <CheckCircle2 className="h-2.5 w-2.5 mr-1 text-emerald-500 inline" /> Ready
                                </Badge>
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-3 pt-1">
                            <div className="flex items-center justify-between text-xs">
                                <span className="text-slate-500">API Gateway</span>
                                <span className="font-mono font-semibold text-slate-800 dark:text-slate-200">
                                    {healthData?.status === "running" ? "127.0.0.1:8000 (Active)" : "Offline"}
                                </span>
                            </div>

                            <Separator />

                            <div className="flex items-center justify-between text-xs">
                                <span className="text-slate-500">Active Model Router</span>
                                <Badge variant="outline" className="font-mono text-[10px] uppercase">
                                    {selectedModel === "auto" ? "Dynamic Router" : selectedModel}
                                </Badge>
                            </div>

                            <Separator />

                            <div className="flex items-center justify-between text-xs">
                                <span className="text-slate-500">Knowledge Engine</span>
                                <span className="font-mono text-slate-800 dark:text-slate-200">ChromaDB + BM25</span>
                            </div>
                        </CardContent>
                    </Card>

                    {/* How to Trigger Diagnostics */}
                    <Card className="border-dashed border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/30">
                        <CardContent className="p-5 text-center space-y-2">
                            <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-xl accent-subtle mb-1">
                                <Cpu className="h-5 w-5" />
                            </div>
                            <h3 className="text-xs font-bold text-slate-900 dark:text-white">
                                Real-Time RAG Trace Ready
                            </h3>
                            <p className="text-[11px] text-slate-500 dark:text-slate-400 leading-relaxed">
                                Ask a question in <strong>AI Assistant</strong> or run an <strong>Autonomous Agent</strong> to stream live tokens, chunk sources, confidence ratings, and latency timings here.
                            </p>
                        </CardContent>
                    </Card>
                </div>
            </aside>
        );
    }

    const {
        request,
        generation,
    } = diagnostics;

    const confidence = Math.round(
        request.confidence * 100,
    );

    const hallucination = Math.round(
        request.hallucination.hallucination_risk *
            100,
    );

    return (
        <aside className="h-full w-80 shrink-0 border-l border-slate-200 bg-white flex flex-col dark:border-slate-800 dark:bg-slate-950">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3.5 dark:border-slate-800">
                <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-indigo-500" />
                    <h2 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
                        Execution Inspector
                    </h2>
                </div>
                <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleInspector}
                    className="h-6 w-6 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200"
                    title="Close Inspector"
                >
                    <X className="h-3.5 w-3.5" />
                </Button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {/* Latest Request Card */}
                <Card className="border border-slate-200 dark:border-slate-800 shadow-sm">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-xs uppercase tracking-wider text-slate-400">
                            Evaluated Query
                        </CardTitle>
                    </CardHeader>

                    <CardContent className="space-y-3 pt-1">
                        <p className="text-xs font-medium text-slate-800 dark:text-slate-200 line-clamp-3">
                            "{request.question}"
                        </p>

                        <Separator />

                        <div className="grid grid-cols-2 gap-2 text-xs">
                            <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 p-2.5">
                                <div className="mb-1 flex items-center gap-1.5 text-slate-500 text-[11px]">
                                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
                                    Confidence
                                </div>
                                <div className="text-base font-bold text-slate-900 dark:text-white">
                                    {confidence}%
                                </div>
                            </div>

                            <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 p-2.5">
                                <div className="mb-1 flex items-center gap-1.5 text-slate-500 text-[11px]">
                                    <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
                                    Hallucination
                                </div>
                                <div className="text-base font-bold text-slate-900 dark:text-white">
                                    {hallucination}%
                                </div>
                            </div>

                            <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 p-2.5">
                                <div className="mb-1 flex items-center gap-1.5 text-slate-500 text-[11px]">
                                    <Clock3 className="h-3.5 w-3.5 text-blue-500" />
                                    Latency
                                </div>
                                <div className="text-base font-bold text-slate-900 dark:text-white">
                                    {(generation.latency_seconds * 1000).toFixed(0)} ms
                                </div>
                            </div>

                            <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-900/50 p-2.5">
                                <div className="mb-1 flex items-center gap-1.5 text-slate-500 text-[11px]">
                                    <Database className="h-3.5 w-3.5 text-purple-500" />
                                    Sources
                                </div>
                                <div className="text-base font-bold text-slate-900 dark:text-white">
                                    {request.citations.source_mapping.length}
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Retrieved Sources Card */}
                <Card className="border border-slate-200 dark:border-slate-800 shadow-sm">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-xs uppercase tracking-wider text-slate-400">
                            Retrieved Chunks ({request.citations.source_mapping.length})
                        </CardTitle>
                    </CardHeader>

                    <CardContent className="space-y-2 pt-1">
                        {request.citations.source_mapping.map((source, index) => (
                            <div
                                key={`${source.chunk_id}-${index}`}
                                className="flex items-start gap-2.5 rounded-lg border border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-900/40 p-2.5 text-xs"
                            >
                                <FileText className="mt-0.5 h-3.5 w-3.5 shrink-0 text-indigo-500" />
                                <div className="min-w-0 flex-1">
                                    <p className="truncate font-semibold text-slate-800 dark:text-slate-200">
                                        {source.filename}
                                    </p>
                                    <p className="text-[10px] text-slate-400">
                                        Chunk {source.chunk_number} of {source.total_chunks}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </CardContent>
                </Card>

                {/* Execution Timings Breakdown */}
                <Card className="border border-slate-200 dark:border-slate-800 shadow-sm">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-xs uppercase tracking-wider text-slate-400">
                            Latency Breakdown
                        </CardTitle>
                    </CardHeader>

                    <CardContent className="space-y-2 text-xs pt-1">
                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                            <span>Vector Retrieval</span>
                            <span className="font-mono">{(request.timings.retrieval_seconds * 1000).toFixed(0)} ms</span>
                        </div>

                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                            <span>Context Assembly</span>
                            <span className="font-mono">{(request.timings.context_build_seconds * 1000).toFixed(0)} ms</span>
                        </div>

                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                            <span>Prompt Build</span>
                            <span className="font-mono">{(request.timings.prompt_build_seconds * 1000).toFixed(0)} ms</span>
                        </div>

                        <div className="flex justify-between text-slate-600 dark:text-slate-400">
                            <span>Ollama LLM Generation</span>
                            <span className="font-mono">{(request.timings.generation_seconds * 1000).toFixed(0)} ms</span>
                        </div>

                        <Separator />

                        <div className="flex justify-between font-bold text-slate-900 dark:text-white pt-1">
                            <span>Total Turnaround</span>
                            <span className="font-mono text-indigo-600 dark:text-indigo-400">{(request.timings.total_seconds * 1000).toFixed(0)} ms</span>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </aside>
    );
}

export default Inspector;