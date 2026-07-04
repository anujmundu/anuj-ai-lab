import {
    useMutation,
    useQueryClient,
} from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { ragService } from "@/services/rag.service";

import type {
    AskRequest,
    AskResponse,
} from "@/types/rag";

export function useAsk() {
    const queryClient =
        useQueryClient();

    return useMutation<
        AskResponse,
        Error,
        AskRequest
    >({
        mutationKey:
            queryKeys.rag.ask,

        mutationFn: (
            request: AskRequest,
        ) => ragService.ask(request),

        async onSuccess() {
            await queryClient.invalidateQueries(
                {
                    queryKey:
                        queryKeys.rag.diagnostics,
                },
            );
        },
    });
}