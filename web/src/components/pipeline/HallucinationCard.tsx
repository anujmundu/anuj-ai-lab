import type { HallucinationInfo } from "@/types/diagnostics";

interface HallucinationCardProps {
    hallucination: HallucinationInfo;
}

export function HallucinationCard({
    hallucination,
}: HallucinationCardProps) {
    return (
        <div className="rounded-lg border bg-card p-4 shadow-sm">
            <h3 className="mb-4 text-sm font-medium text-muted-foreground">
                Hallucination Analysis
            </h3>

            <div className="grid gap-3 md:grid-cols-2">
                <div>
                    <p className="text-xs text-muted-foreground">
                        Hallucination Risk
                    </p>

                    <p className="text-xl font-semibold">
                        {(hallucination.hallucination_risk * 100).toFixed(0)}%
                    </p>
                </div>

                <div>
                    <p className="text-xs text-muted-foreground">
                        Context Overlap
                    </p>

                    <p className="text-xl font-semibold">
                        {(hallucination.context_overlap * 100).toFixed(0)}%
                    </p>
                </div>

                <div>
                    <p className="text-xs text-muted-foreground">
                        Supported Terms
                    </p>

                    <p className="text-xl font-semibold">
                        {hallucination.supported_terms}
                    </p>
                </div>

                <div>
                    <p className="text-xs text-muted-foreground">
                        Unsupported Terms
                    </p>

                    <p className="text-xl font-semibold">
                        {hallucination.unsupported_terms}
                    </p>
                </div>
            </div>

            <div className="mt-5">
                <p className="text-xs text-muted-foreground">
                    Potential Hallucination
                </p>

                <p className="font-semibold">
                    {hallucination.is_potential_hallucination
                        ? "Yes"
                        : "No"}
                </p>
            </div>

            <div className="mt-5">
                <p className="text-xs text-muted-foreground">
                    Unsupported Terms
                </p>

                <div className="mt-2 flex flex-wrap gap-2">
                    {hallucination.unsupported_term_list.map((term) => (
                        <span
                            key={term}
                            className="rounded-md border px-2 py-1 text-xs"
                        >
                            {term}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
}