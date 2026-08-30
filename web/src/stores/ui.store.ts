import { create } from "zustand";

export type AccentColor =
    | "indigo"
    | "emerald"
    | "cyan"
    | "violet"
    | "amber"
    | "rose"
    | "sapphire"
    | "sunset"
    | "teal"
    | "fuchsia"
    | "lime"
    | "slate";

export type ThemeMode =
    | "light"
    | "dark"
    | "cyberpunk"
    | "forest"
    | "espresso"
    | "ocean"
    | "amethyst"
    | "crimson"
    | "sunset_glow"
    | "sepia"
    | "arctic"
    | "system";

interface UIState {
    sidebarOpen: boolean;
    toggleSidebar: () => void;
    setSidebarOpen: (open: boolean) => void;
    inspectorOpen: boolean;
    toggleInspector: () => void;
    setInspectorOpen: (open: boolean) => void;
    accentColor: AccentColor;
    setAccentColor: (color: AccentColor) => void;
    themeMode: ThemeMode;
    setThemeMode: (mode: ThemeMode) => void;
    selectedModel: string;
    setSelectedModel: (model: string) => void;
}

const savedAccent = (localStorage.getItem("app_accent") as AccentColor) || "indigo";
const savedThemeMode = (localStorage.getItem("app_theme_mode") as ThemeMode) || "dark";
const savedInspector = localStorage.getItem("app_inspector") !== "false";

function applyThemeToDocument(mode: ThemeMode, accent: AccentColor) {
    if (typeof document === "undefined") return;
    const root = document.documentElement;

    root.setAttribute("data-accent", accent);
    root.setAttribute("data-theme-mode", mode);

    // Manage dark class for Tailwind
    const isDark =
        mode === "dark" ||
        mode === "cyberpunk" ||
        mode === "forest" ||
        mode === "espresso" ||
        mode === "ocean" ||
        mode === "amethyst" ||
        mode === "crimson" ||
        mode === "sunset_glow" ||
        (mode === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);

    if (isDark) {
        root.classList.add("dark");
    } else {
        root.classList.remove("dark");
    }
}

if (typeof document !== "undefined") {
    applyThemeToDocument(savedThemeMode, savedAccent);
}

export const useUIStore = create<UIState>((set) => ({
    sidebarOpen: true,
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    setSidebarOpen: (open) => set({ sidebarOpen: open }),
    inspectorOpen: savedInspector,
    toggleInspector: () =>
        set((state) => {
            const next = !state.inspectorOpen;
            localStorage.setItem("app_inspector", String(next));
            return { inspectorOpen: next };
        }),
    setInspectorOpen: (open) => {
        localStorage.setItem("app_inspector", String(open));
        set({ inspectorOpen: open });
    },
    accentColor: savedAccent,
    setAccentColor: (color) => {
        localStorage.setItem("app_accent", color);
        set((state) => {
            applyThemeToDocument(state.themeMode, color);
            return { accentColor: color };
        });
    },
    themeMode: savedThemeMode,
    setThemeMode: (mode) => {
        localStorage.setItem("app_theme_mode", mode);
        set((state) => {
            applyThemeToDocument(mode, state.accentColor);
            return { themeMode: mode };
        });
    },
    selectedModel: "auto",
    setSelectedModel: (model) => set({ selectedModel: model }),
}));
