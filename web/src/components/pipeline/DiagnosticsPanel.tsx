import type { DiagnosticsResponse } from "@/types/diagnostics";

import { CitationCard } from "./CitationCard";
import { ConfidenceCard } from "./ConfidenceCard";
import { HallucinationCard } from "./HallucinationCard";
import { TimingCard } from "./TimingCard";

interface DiagnosticsPanelProps {
    diagnostics?: DiagnosticsResponse;
    isLoading: boolean;
}

export function DiagnosticsPanel({
    diagnostics,
    isLoading,
}: DiagnosticsPanelProps) {
    if (isLoading) {
        return (
            <p className="text-sm text-muted-foreground">
                Loading diagnostics...
            </p>
        );
    }

    if (!diagnostics || !diagnostics.request.question) {
        return (
            <p className="text-sm text-muted-foreground">
                No diagnostics available.
            </p>
        );
    }

    const timings = diagnostics.request.timings;

    return (
        <div className="flex flex-col gap-6">
            <div className="rounded-lg border bg-card p-4 shadow-sm">
                <h2 className="text-lg font-semibold">
                    Latest Request
                </h2>

                <p className="mt-2 text-sm text-muted-foreground">
                    {diagnostics.request.question}
                </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                <TimingCard
                    label="Retrieval"
                    seconds={timings.retrieval_seconds}
                />

                <TimingCard
                    label="Context Build"
                    seconds={timings.context_build_seconds}
                />

                <TimingCard
                    label="Prompt Build"
                    seconds={timings.prompt_build_seconds}
                />

                <TimingCard
                    label="Generation"
                    seconds={timings.generation_seconds}
                />

                <TimingCard
                    label="Total"
                    seconds={timings.total_seconds}
                />

                <ConfidenceCard
                    confidence={diagnostics.request.confidence}
                />
            </div>

            <HallucinationCard
                hallucination={
                    diagnostics.request.hallucination
                }
            />

            <CitationCard
                citations={
                    diagnostics.request.citations
                }
            />
        </div>
    );
}