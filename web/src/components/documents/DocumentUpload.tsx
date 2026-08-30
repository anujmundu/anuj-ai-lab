import { useState, useEffect, useRef } from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { Loader2, CheckCircle2, AlertCircle, Sparkles } from "lucide-react";
import { useIngestDocument } from "@/hooks";
import { queryKeys } from "@/lib/query-keys";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { UploadDropzone } from "./UploadDropzone";

interface ActiveJob {
    jobId: string;
    filename: string;
    status: "queued" | "running" | "completed" | "failed";
    progress: number;
    error?: string | null;
}

export function DocumentUpload() {
    const [file, setFile] = useState<File | null>(null);
    const [activeJob, setActiveJob] = useState<ActiveJob | null>(null);
    const ingestMutation = useIngestDocument();
    const queryClient = useQueryClient();
    const pollTimerRef = useRef<number | null>(null);

    // Poll active ingestion job
    useEffect(() => {
        if (!activeJob || activeJob.status === "completed" || activeJob.status === "failed") {
            if (pollTimerRef.current) {
                clearInterval(pollTimerRef.current);
                pollTimerRef.current = null;
            }
            return;
        }

        const pollJob = async () => {
            try {
                const { data } = await api.get(`/ingestion/jobs/${activeJob.jobId}`);
                if (data) {
                    setActiveJob((prev) =>
                        prev
                            ? {
                                  ...prev,
                                  status: data.status,
                                  progress: data.progress ?? (data.status === "completed" ? 1.0 : 0.5),
                                  error: data.error,
                              }
                            : null
                    );

                    if (data.status === "completed") {
                        await queryClient.invalidateQueries({ queryKey: queryKeys.documents.all });
                        toast.success(`Successfully indexed '${activeJob.filename}' into ChromaDB & BM25!`);
                        setTimeout(() => setActiveJob(null), 3000);
                    } else if (data.status === "failed") {
                        toast.error(`Indexing failed for '${activeJob.filename}': ${data.error || "Unknown error"}`);
                    }
                }
            } catch (err: any) {
                console.error("Job poll error:", err);
            }
        };

        pollTimerRef.current = window.setInterval(pollJob, 1000);
        return () => {
            if (pollTimerRef.current) {
                clearInterval(pollTimerRef.current);
            }
        };
    }, [activeJob?.jobId, activeJob?.status, queryClient]);

    async function handleUpload() {
        if (!file) return;

        const targetFile = file;
        try {
            const res = await ingestMutation.mutateAsync(targetFile);
            setFile(null);
            if (res && res.job_id) {
                setActiveJob({
                    jobId: res.job_id,
                    filename: targetFile.name,
                    status: (res.job_status as any) || "queued",
                    progress: 0.1,
                });
            } else {
                await queryClient.invalidateQueries({ queryKey: queryKeys.documents.all });
                toast.success(`Document '${targetFile.name}' uploaded successfully.`);
            }
        } catch (error: any) {
            toast.error(error.message || "Document upload failed.");
        }
    }

    return (
        <Card>
            <CardContent className="space-y-6 pt-6">
                <UploadDropzone
                    selectedFile={file}
                    onFileSelect={setFile}
                    disabled={ingestMutation.isPending || (!!activeJob && activeJob.status !== "completed" && activeJob.status !== "failed")}
                />

                {/* Active Ingestion Progress Tracker */}
                {activeJob && (
                    <div className="p-4 rounded-xl border border-indigo-200 dark:border-indigo-950 bg-indigo-50/50 dark:bg-indigo-950/20 space-y-3">
                        <div className="flex items-center justify-between text-xs">
                            <div className="flex items-center gap-2 font-medium text-indigo-950 dark:text-indigo-200">
                                {activeJob.status === "completed" ? (
                                    <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                                ) : activeJob.status === "failed" ? (
                                    <AlertCircle className="h-4 w-4 text-red-500" />
                                ) : (
                                    <Loader2 className="h-4 w-4 text-indigo-600 animate-spin" />
                                )}
                                <span>
                                    {activeJob.status === "completed"
                                        ? `Indexed: ${activeJob.filename}`
                                        : activeJob.status === "failed"
                                        ? `Failed: ${activeJob.filename}`
                                        : `Indexing & Vectorizing: ${activeJob.filename}`}
                                </span>
                            </div>

                            <div className="flex items-center gap-2">
                                <Badge
                                    variant={
                                        activeJob.status === "completed"
                                            ? "default"
                                            : activeJob.status === "failed"
                                            ? "destructive"
                                            : "secondary"
                                    }
                                    className="text-[10px] uppercase font-mono tracking-wider"
                                >
                                    {activeJob.status}
                                </Badge>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => setActiveJob(null)}
                                    className="h-5 px-1.5 text-[10px] text-slate-500 hover:text-slate-900"
                                >
                                    Dismiss
                                </Button>
                            </div>
                        </div>

                        <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-1.5 overflow-hidden">
                            <div
                                className="bg-indigo-600 h-1.5 rounded-full transition-all duration-500"
                                style={{ width: `${activeJob.status === "completed" ? 100 : Math.round(activeJob.progress * 100) || 35}%` }}
                            />
                        </div>

                        {activeJob.error && (
                            <p className="text-xs text-red-600 dark:text-red-400 font-mono">
                                Error: {activeJob.error}
                            </p>
                        )}
                    </div>
                )}

                <div className="flex flex-wrap items-center gap-3">
                    <Button
                        onClick={handleUpload}
                        disabled={!file || ingestMutation.isPending || (!!activeJob && activeJob.status !== "completed" && activeJob.status !== "failed")}
                        className="flex items-center gap-2"
                    >
                        {ingestMutation.isPending ? (
                            <>
                                <Loader2 className="h-4 w-4 animate-spin" />
                                Uploading...
                            </>
                        ) : (
                            <>
                                <Sparkles className="h-4 w-4" />
                                Upload & Vectorize
                            </>
                        )}
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}