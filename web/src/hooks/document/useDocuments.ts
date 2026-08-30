import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { documentService } from "@/services/document.service";

export function useDocuments() {
    return useQuery({
        queryKey: queryKeys.documents.all,
        queryFn: () => documentService.getDocuments(),
        refetchInterval: 2500, // Auto-refresh every 2.5s for background ingestion jobs
    });
}