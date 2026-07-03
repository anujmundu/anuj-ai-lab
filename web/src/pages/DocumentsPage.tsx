import { DocumentList } from "@/components/documents";
import { useDocuments } from "@/hooks";

export default function DocumentsPage() {
    const {
        data = [],
        isLoading,
        error,
    } = useDocuments();

    console.log("DocumentsPage", {
        data,
        isLoading,
        error,
    });

    return (
        <section className="flex flex-1 flex-col gap-6 p-6">
            <div>
                <h1 className="text-2xl font-bold">
                    Documents
                </h1>

                <p className="text-muted-foreground">
                    Indexed knowledge base
                </p>
            </div>

            <DocumentList
                documents={data}
                isLoading={isLoading}
            />
        </section>
    );
}