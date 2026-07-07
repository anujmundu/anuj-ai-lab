import { useMutation } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { memoryService } from "@/services/memory.service";

export function useUpdateMemory() {
    const queryClient =
        useQueryClient();

    return useMutation({
        mutationFn: ({
            id,
            memory,
        }: {
            id: number;
            memory: Parameters<
                typeof memoryService.update
            >[1];
        }) =>
            memoryService.update(
                id,
                memory,
            ),

        onSuccess: () => {
            queryClient.invalidateQueries({
                queryKey:
                    queryKeys.memory.all,
            });

            queryClient.invalidateQueries({
                queryKey: [
                    "memory",
                    "search",
                ],
            });
        },
    });
}