import { RefreshCw, FileText } from "lucide-react";
import {
    DocumentList,
    DocumentUpload,
} from "@/components/documents";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useDocuments } from "@/hooks";

export default function DocumentsPage() {
    const {
        data = [],
        isLoading,
        refetch,
    } = useDocuments();

    return (
        <section className="flex flex-1 flex-col gap-8 p-6 overflow-y-auto w-full">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md">
                        <FileText className="h-5 w-5" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                            Knowledge Base Documents
                        </h1>
                        <p className="text-slate-500 dark:text-slate-400 text-sm">
                            Upload documents (PDF, TXT, MD, DOCX) to vectorize into ChromaDB and build hybrid BM25 indexes.
                        </p>
                    </div>
                </div>

                <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => refetch()} 
                    className="flex items-center gap-1.5 text-xs"
                >
                    <RefreshCw className="h-3.5 w-3.5" /> Refresh Index
                </Button>
            </div>

            <DocumentUpload />

            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                            Indexed Documents ({data.length})
                        </h2>
                        <p className="text-xs text-muted-foreground">
                            Documents actively parsed, chunked, and searchable in the RAG pipeline.
                        </p>
                    </div>
                    <Badge variant="outline" className="text-xs font-mono">
                        ChromaDB Shard 0
                    </Badge>
                </div>

                <DocumentList
                    documents={data}
                    isLoading={isLoading}
                />
            </div>
        </section>
    );
}