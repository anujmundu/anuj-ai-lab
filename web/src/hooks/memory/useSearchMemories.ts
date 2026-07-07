import { useQuery } from "@tanstack/react-query";

import { queryKeys } from "@/lib/query-keys";
import { memoryService } from "@/services/memory.service";

export function useSearchMemories(
    query: string,
) {
    return useQuery({
        queryKey: queryKeys.memory.search(query),
        queryFn: () =>
            memoryService.search(query),
        enabled: query.length > 0,
    });
}