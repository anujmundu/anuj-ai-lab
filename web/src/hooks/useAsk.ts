import { useMutation } from "@tanstack/react-query";

import { ragService } from "@/services/rag.service";

import type { AskRequest } from "@/types/rag";

export function useAsk() {
    return useMutation({
        mutationFn: (request: AskRequest) =>
            ragService.ask(request),
    });
}