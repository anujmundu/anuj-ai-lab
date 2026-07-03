import type { DocumentInfo } from "@/types/document";

interface DocumentCardProps {
    document: DocumentInfo;
}

export function DocumentCard({
    document,
}: DocumentCardProps) {
    console.log(
        "[DocumentCard]",
        document,
    );

    return (
        <div className="rounded-lg border bg-card p-4 shadow-sm">
            <h3 className="text-base font-semibold">
                {document.filename}
            </h3>

            <p className="mt-2 text-sm text-muted-foreground">
                {document.chunks} chunk
                {document.chunks === 1 ? "" : "s"}
            </p>
        </div>
    );
}