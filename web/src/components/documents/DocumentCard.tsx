import type { DocumentInfo } from "@/types/document";

interface DocumentCardProps {
    document: DocumentInfo;
}

export function DocumentCard({
    document,
}: DocumentCardProps) {
    return (
        <div className="rounded-xl border bg-card p-5 shadow-sm transition-shadow hover:shadow-md">
            <div className="flex items-start justify-between">
                <div>
                    <h3 className="text-lg font-semibold">
                        📄 {document.filename}
                    </h3>

                    <p className="mt-2 text-sm text-muted-foreground">
                        {document.chunks} chunk
                        {document.chunks === 1
                            ? ""
                            : "s"}{" "}
                        indexed
                    </p>
                </div>
            </div>
        </div>
    );
}