import { Trash2 } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useDeleteDocument } from "@/hooks/document/useDeleteDocument";
import type { DocumentInfo } from "@/types/document";

interface DocumentCardProps {
    document: DocumentInfo;
}

export function DocumentCard({
    document,
}: DocumentCardProps) {
    const deleteMutation = useDeleteDocument();

    function handleDelete() {
        if (!confirm(`Are you sure you want to remove '${document.filename}' from the index?`)) {
            return;
        }

        deleteMutation.mutate(document.filename, {
            onSuccess() {
                toast.success(`Removed ${document.filename} from index.`);
            },
            onError(err) {
                toast.error(err.message || "Failed to delete document.");
            },
        });
    }

    return (
        <div className="rounded-xl border bg-card p-5 shadow-sm transition-shadow hover:shadow-md flex items-center justify-between">
            <div>
                <div className="flex items-center gap-2">
                    <h3 className="text-base font-semibold">
                        📄 {document.filename}
                    </h3>
                    <Badge variant="secondary" className="text-xs">
                        Indexed
                    </Badge>
                </div>

                <p className="mt-1 text-xs text-muted-foreground">
                    {document.chunks} chunk{document.chunks === 1 ? "" : "s"} indexed in ChromaDB & BM25
                </p>
            </div>

            <Button
                variant="ghost"
                size="icon"
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
                className="text-slate-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/50"
                aria-label={`Delete ${document.filename}`}
            >
                <Trash2 className="h-4 w-4" />
            </Button>
        </div>
    );
}