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
    console.log(
        "[DocumentList]",
        documents,
    );

    if (isLoading) {
        return (
            <p className="text-sm text-muted-foreground">
                Loading documents...
            </p>
        );
    }

    if (documents.length === 0) {
        return (
            <p className="text-sm text-muted-foreground">
                No documents indexed.
            </p>
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