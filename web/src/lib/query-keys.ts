export const queryKeys = {

    memory: {
        all: [
            "memory",
        ] as const,

        detail: (
            id: number,
        ) =>
            [
                "memory",
                id,
            ] as const,

        search: (
            query: string,
        ) =>
            [
                "memory",
                "search",
                query,
            ] as const,
    },

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

        upload: [
            "documents",
            "upload",
        ] as const,

        recent: [
            "documents",
            "recent",
        ] as const,

        versions: (
            filename: string,
        ) =>
            [
                "documents",
                filename,
                "versions",
            ] as const,
    },

    system: {
        health: [
            "system",
            "health",
        ] as const,

        settings: [
            "system",
            "settings",
        ] as const,

        models: [
            "system",
            "models",
        ] as const,
    },
} as const;