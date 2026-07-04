import type { DocumentInfo } from "@/types/document";

import { DocumentCard } from "./DocumentCard";

interface DocumentListProps {
    documents?: DocumentInfo[];
    isLoading: boolean;
}

export function DocumentList({
    documents = [],
    isLoading,
}: DocumentListProps) {
    if (isLoading) {
        return (
            <div className="rounded-lg border bg-card p-6">
                <p className="text-sm text-muted-foreground">
                    Loading documents...
                </p>
            </div>
        );
    }

    if (documents.length === 0) {
        return (
            <div className="rounded-lg border bg-card p-6">
                <p className="text-sm text-muted-foreground">
                    No documents indexed yet.
                </p>
            </div>
        );
    }

    return (
        <div className="grid gap-4">
            {documents.map((document) => (
                <DocumentCard
                    key={document.filename}
                    document={document}
                />
            ))}
        </div>
    );
}