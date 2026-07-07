import { useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { memoryService } from "@/services/memory.service";

export function useCreateMemory() {
    const queryClient =
        useQueryClient();

    return useMutation({
        mutationFn: memoryService.create,

        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey:
                    queryKeys.memory.all,
            });
        },
    });
}