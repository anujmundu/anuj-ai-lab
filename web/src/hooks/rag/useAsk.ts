import { useMutation } from "@tanstack/react-query";

import { ragService } from "@/services/rag.service";
import { queryKeys } from "@/lib/query-keys";

import type {
    AskRequest,
    AskResponse,
} from "@/types/rag";

export function useAsk() {
    return useMutation<
        AskResponse,
        Error,
        AskRequest
    >({
        mutationKey: queryKeys.rag.ask,

        mutationFn: (
            request: AskRequest,
        ) => ragService.ask(request),
    });
}