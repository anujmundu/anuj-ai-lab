import { useState } from "react";
import { Search, FileText } from "lucide-react";
import type { DocumentInfo } from "@/types/document";
import { DocumentCard } from "./DocumentCard";
import { Input } from "@/components/ui/input";

interface DocumentListProps {
    documents?: DocumentInfo[];
    isLoading: boolean;
}

export function DocumentList({
    documents = [],
    isLoading,
}: DocumentListProps) {
    const [search, setSearch] = useState("");

    const filtered = documents.filter((d) =>
        d.filename.toLowerCase().includes(search.toLowerCase())
    );

    if (isLoading && documents.length === 0) {
        return (
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-card p-8 text-center">
                <p className="text-sm text-muted-foreground animate-pulse">
                    Loading indexed knowledge base...
                </p>
            </div>
        );
    }

    if (documents.length === 0) {
        return (
            <div className="rounded-xl border border-dashed border-slate-200 dark:border-slate-800 bg-card p-10 text-center space-y-2">
                <FileText className="h-10 w-10 text-slate-300 mx-auto mb-2" />
                <h3 className="font-semibold text-sm text-slate-800 dark:text-slate-200">No Documents Indexed Yet</h3>
                <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                    Upload your first document (PDF, TXT, MD, CSV, JSON) above to automatically parse, chunk, and index it into ChromaDB.
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {documents.length > 3 && (
                <div className="relative">
                    <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                    <Input
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search indexed documents..."
                        className="pl-9 text-xs"
                    />
                </div>
            )}

            <div className="grid gap-3">
                {filtered.length === 0 ? (
                    <div className="rounded-xl border p-6 text-center text-xs text-slate-400">
                        No documents match your filter "{search}".
                    </div>
                ) : (
                    filtered.map((document) => (
                        <DocumentCard
                            key={document.filename}
                            document={document}
                        />
                    ))
                )}
            </div>
        </div>
    );
}