export const queryKeys = {

    rag: {

        search: (
            query: string,
            k: number,
        ) => [
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

    },

} as const;