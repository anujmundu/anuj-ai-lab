import {
    useMutation,
    useQueryClient,
} from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { documentService } from "@/services/document.service";

import type { IngestResponse } from "@/types/document";

export function useIngestDocument() {
    const queryClient =
        useQueryClient();

    return useMutation<
        IngestResponse,
        Error,
        File
    >({
        mutationFn: (
            file: File,
        ) =>
            documentService.ingest(
                file,
            ),

        async onSuccess() {
            await queryClient.invalidateQueries(
                {
                    queryKey:
                        queryKeys.documents.all,
                },
            );
        },
    });
}