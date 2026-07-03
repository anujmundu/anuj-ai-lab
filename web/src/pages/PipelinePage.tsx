import { DiagnosticsPanel } from "@/components/pipeline";
import { useDiagnostics } from "@/hooks";

export default function PipelinePage() {
    const {
        data,
        isLoading,
    } = useDiagnostics();

    return (
        <section className="flex flex-1 flex-col gap-6 p-6">
            <div>
                <h1 className="text-2xl font-bold">
                    Pipeline Diagnostics
                </h1>

                <p className="text-muted-foreground">
                    Latest Retrieval-Augmented Generation execution
                </p>
            </div>

            <DiagnosticsPanel
                diagnostics={data}
                isLoading={isLoading}
            />
        </section>
    );
}