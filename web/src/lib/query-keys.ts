export const queryKeys = {
    rag: {
        ask: [
            "rag",
            "ask",
        ] as const,

        search: (
            query: string,
            k: number,
        ) =>
            [
                "rag",
                "search",
                query,
                k,
            ] as const,

        diagnostics: [
            "rag",
            "diagnostics",
        ] as const,
    },

    documents: {
        all: [
            "documents",
        ] as const,

        detail: (
            filename: string,
        ) =>
            [
                "documents",
                filename,
            ] as const,
    },
} as const;