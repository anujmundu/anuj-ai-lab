import {
    useMutation,
    useQueryClient,
} from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { documentService } from "@/services/document.service";

export function useDeleteDocument() {
    const queryClient =
        useQueryClient();

    return useMutation<
        void,
        Error,
        string
    >({
        mutationFn: (
            filename: string,
        ) =>
            documentService.deleteDocument(
                filename,
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