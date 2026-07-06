import {
    Activity,
    AlertTriangle,
    Clock3,
    Database,
    FileText,
    ShieldCheck,
} from "lucide-react";

import { useLatestDiagnostics } from "@/hooks";

import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export function Inspector() {
    const diagnostics = useLatestDiagnostics();

    if (!diagnostics) {
        return (
            <aside className="hidden h-full w-80 shrink-0 border-l border-slate-200 bg-white xl:flex xl:flex-col dark:border-slate-800 dark:bg-slate-950">
                <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
                    <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                        Inspector
                    </h2>
                </div>

                <div className="flex flex-1 items-center justify-center p-6">
                    <Card className="w-full border-dashed">
                        <CardContent className="p-8">
                            <div className="flex flex-col items-center text-center">
                                <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 dark:bg-slate-900">
                                    <Activity className="h-7 w-7 text-slate-500" />
                                </div>

                                <h3 className="text-lg font-semibold">
                                    No inspection available
                                </h3>

                                <p className="mt-2 text-sm text-slate-500">
                                    Ask a question or run a workflow to inspect
                                    diagnostics, sources, confidence and
                                    execution statistics.
                                </p>
                            </div>
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
        <aside className="hidden h-full w-80 shrink-0 border-l border-slate-200 bg-white xl:flex xl:flex-col dark:border-slate-800 dark:bg-slate-950">
            <div className="border-b border-slate-200 px-5 py-4 dark:border-slate-800">
                <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
                    Inspector
                </h2>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
                <div className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">
                                Latest Request
                            </CardTitle>
                        </CardHeader>

                        <CardContent className="space-y-4">
                            <p className="text-sm">
                                {request.question}
                            </p>

                            <Separator />

                            <div className="grid grid-cols-2 gap-3 text-sm">
                                <div className="rounded-lg border p-3">
                                    <div className="mb-2 flex items-center gap-2 text-slate-500">
                                        <ShieldCheck className="h-4 w-4" />
                                        Confidence
                                    </div>

                                    <div className="text-lg font-semibold">
                                        {confidence}%
                                    </div>
                                </div>

                                <div className="rounded-lg border p-3">
                                    <div className="mb-2 flex items-center gap-2 text-slate-500">
                                        <AlertTriangle className="h-4 w-4" />
                                        Hallucination
                                    </div>

                                    <div className="text-lg font-semibold">
                                        {hallucination}%
                                    </div>
                                </div>

                                <div className="rounded-lg border p-3">
                                    <div className="mb-2 flex items-center gap-2 text-slate-500">
                                        <Clock3 className="h-4 w-4" />
                                        Latency
                                    </div>

                                    <div className="text-lg font-semibold">
                                        {(
                                            generation.latency_seconds *
                                            1000
                                        ).toFixed(
                                            0,
                                        )}{" "}
                                        ms
                                    </div>
                                </div>

                                <div className="rounded-lg border p-3">
                                    <div className="mb-2 flex items-center gap-2 text-slate-500">
                                        <Database className="h-4 w-4" />
                                        Sources
                                    </div>

                                    <div className="text-lg font-semibold">
                                        {
                                            request.citations
                                                .source_mapping
                                                .length
                                        }
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">
                                Retrieved Sources
                            </CardTitle>
                        </CardHeader>

                        <CardContent className="space-y-3">
                            {request.citations.source_mapping.map(
                                (
                                    source,
                                    index,
                                ) => (
                                    <div
                                        key={`${source.chunk_id}-${index}`}
                                        className="flex items-start gap-2 rounded-lg border p-3"
                                    >
                                        <FileText className="mt-0.5 h-4 w-4 shrink-0 text-slate-500" />

                                        <div className="min-w-0">
                                            <p className="truncate text-sm font-medium">
                                                {
                                                    source.filename
                                                }
                                            </p>

                                            <p className="text-xs text-slate-500">
                                                Chunk{" "}
                                                {
                                                    source.chunk_number
                                                }
                                                /
                                                {
                                                    source.total_chunks
                                                }
                                            </p>
                                        </div>
                                    </div>
                                ),
                            )}
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">
                                Execution
                            </CardTitle>
                        </CardHeader>

                        <CardContent className="space-y-3 text-sm">
                            <div className="flex justify-between">
                                <span>
                                    Retrieval
                                </span>

                                <span>
                                    {(
                                        request
                                            .timings
                                            .retrieval_seconds *
                                        1000
                                    ).toFixed(
                                        0,
                                    )}{" "}
                                    ms
                                </span>
                            </div>

                            <div className="flex justify-between">
                                <span>
                                    Context
                                </span>

                                <span>
                                    {(
                                        request
                                            .timings
                                            .context_build_seconds *
                                        1000
                                    ).toFixed(
                                        0,
                                    )}{" "}
                                    ms
                                </span>
                            </div>

                            <div className="flex justify-between">
                                <span>
                                    Prompt
                                </span>

                                <span>
                                    {(
                                        request
                                            .timings
                                            .prompt_build_seconds *
                                        1000
                                    ).toFixed(
                                        0,
                                    )}{" "}
                                    ms
                                </span>
                            </div>

                            <div className="flex justify-between">
                                <span>
                                    Generation
                                </span>

                                <span>
                                    {(
                                        request
                                            .timings
                                            .generation_seconds *
                                        1000
                                    ).toFixed(
                                        0,
                                    )}{" "}
                                    ms
                                </span>
                            </div>

                            <Separator />

                            <div className="flex justify-between font-semibold">
                                <span>Total</span>

                                <span>
                                    {(
                                        request
                                            .timings
                                            .total_seconds *
                                        1000
                                    ).toFixed(
                                        0,
                                    )}{" "}
                                    ms
                                </span>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </aside>
    );
}

export default Inspector;