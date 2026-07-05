import type { ReactNode } from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";

interface ThemeProviderProps {
    children: ReactNode;
}

export function ThemeProvider({
    children,
}: ThemeProviderProps) {
    return (
        <NextThemesProvider
            attribute="class"
            defaultTheme="system"
            enableSystem={false}
            storageKey="anuj-ai-lab-theme"
            disableTransitionOnChange
        >
            {children}
        </NextThemesProvider>
    );
}