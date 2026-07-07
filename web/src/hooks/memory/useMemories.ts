import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { memoryService } from "@/services/memory.service";

export function useMemories() {
    return useQuery({
        queryKey: queryKeys.memory.all,
        queryFn: () => memoryService.getAll(),
    });
}