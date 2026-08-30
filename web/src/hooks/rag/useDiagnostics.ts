import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { diagnosticsService } from "@/services/diagnostics.service";

export function useDiagnostics() {
    return useQuery({
        queryKey: queryKeys.rag.diagnostics,

        queryFn: () =>
            diagnosticsService.getDiagnostics(),

        refetchOnMount: "always",

        refetchOnWindowFocus: true,

        refetchInterval: 3000,

        staleTime: 1000,
    });
}