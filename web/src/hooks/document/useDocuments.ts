import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { documentService } from "@/services/document.service";

export function useDocuments() {
    return useQuery({
        queryKey: queryKeys.documents.all,

        queryFn: async () => {
            const documents =
                await documentService.getDocuments();

            console.log(
                "[useDocuments]",
                documents,
            );

            return documents;
        },
    });
}