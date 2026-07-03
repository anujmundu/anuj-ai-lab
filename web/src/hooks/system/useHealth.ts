import { useQuery } from "@tanstack/react-query";

import { healthService } from "@/services/system/health.service";

export function useHealth() {
    return useQuery({
        queryKey: ["health"],

        queryFn: () =>
            healthService.getHealth(),

        retry: 1,

        refetchInterval: 5000,

        staleTime: 5000,
    });
}