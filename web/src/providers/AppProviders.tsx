import type { ReactNode } from "react";

import { Toaster } from "sonner";

import { QueryProvider } from "./QueryProvider";
import { ThemeProvider } from "./ThemeProvider";

interface AppProvidersProps {
    children: ReactNode;
}

export function AppProviders({
    children,
}: AppProvidersProps) {
    return (
        <ThemeProvider>
            <QueryProvider>
                {children}

                <Toaster
                    richColors
                    position="top-right"
                    closeButton
                />
            </QueryProvider>
        </ThemeProvider>
    );
}