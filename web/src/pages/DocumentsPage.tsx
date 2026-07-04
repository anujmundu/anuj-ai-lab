import {
    DocumentList,
    DocumentUpload,
} from "@/components/documents";

import { useDocuments } from "@/hooks";

export default function DocumentsPage() {
    const {
        data = [],
        isLoading,
    } = useDocuments();

    return (
        <section className="flex flex-1 flex-col gap-8 p-6">
            <div>
                <h1 className="text-2xl font-bold">
                    Documents
                </h1>

                <p className="text-muted-foreground">
                    Indexed knowledge base
                </p>
            </div>

            <DocumentUpload />

            <div className="space-y-4">
                <div>
                    <h2 className="text-xl font-semibold">
                        Indexed Documents
                    </h2>

                    <p className="text-sm text-muted-foreground">
                        Documents currently available to the
                        Retrieval-Augmented Generation pipeline.
                    </p>
                </div>

                <DocumentList
                    documents={data}
                    isLoading={isLoading}
                />
            </div>
        </section>
    );
}