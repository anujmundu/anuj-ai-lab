import { useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";

import type { DiagnosticsResponse } from "@/types/diagnostics";

export function useLatestDiagnostics() {
    const queryClient = useQueryClient();

    return queryClient.getQueryData<DiagnosticsResponse>(
        queryKeys.rag.diagnostics,
    );
}