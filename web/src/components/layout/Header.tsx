import { useState, useRef, useEffect } from "react";
import {
    Cpu,
    Menu,
    Settings,
    PanelLeftClose,
    PanelLeftOpen,
    Palette,
    Sparkles,
    Sun,
    Moon,
    Trees,
    Coffee,
    Waves,
    Gem,
    Flame,
    Sunset,
    BookOpen,
    Snowflake,
    Monitor,
    Check,
    ChevronDown,
    ArrowLeft
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";

import { useHealth } from "@/hooks/system/useHealth";
import { useUIStore, type AccentColor, type ThemeMode } from "@/stores";
import { MobileSidebar } from "@/components/navigation/MobileSidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

const THEME_MODES: { id: ThemeMode; label: string; desc: string; icon: any }[] = [
    { id: "light", label: "Pure Light", desc: "Crisp daylight with slate contrast", icon: Sun },
    { id: "dark", label: "Midnight Obsidian", desc: "Deep dark with sleek borders", icon: Moon },
    { id: "cyberpunk", label: "Cyberpunk Void", desc: "Ultra-dark with glowing neon", icon: Sparkles },
    { id: "forest", label: "Nordic Forest", desc: "Organic emerald & deep spruce", icon: Trees },
    { id: "espresso", label: "Velvet Espresso", desc: "Warm mocha & rich roasted tones", icon: Coffee },
    { id: "ocean", label: "Ocean Depths", desc: "Nautical abyss & deep navy", icon: Waves },
    { id: "amethyst", label: "Royal Amethyst", desc: "Regal dark violet & dusk purple", icon: Gem },
    { id: "crimson", label: "Crimson Eclipse", desc: "Bold blood-moon & charcoal", icon: Flame },
    { id: "sunset_glow", label: "Sunset Dusk", desc: "Warm amber dusk & golden shadows", icon: Sunset },
    { id: "sepia", label: "Vintage Sepia", desc: "Warm antique book parchment", icon: BookOpen },
    { id: "arctic", label: "Arctic Frost", desc: "Cool glacier ice & polar slate", icon: Snowflake },
    { id: "system", label: "System Adaptive", desc: "Synchronizes with device OS", icon: Monitor },
];

const ACCENT_COLORS: { id: AccentColor; label: string; class: string; hex: string }[] = [
    { id: "indigo", label: "Electric Indigo", class: "bg-indigo-600", hex: "#4f46e5" },
    { id: "emerald", label: "Vibrant Emerald", class: "bg-emerald-600", hex: "#059669" },
    { id: "cyan", label: "Neon Cyan", class: "bg-cyan-500", hex: "#06b6d4" },
    { id: "violet", label: "Deep Violet", class: "bg-purple-600", hex: "#9333ea" },
    { id: "amber", label: "Amber Gold", class: "bg-amber-500", hex: "#f59e0b" },
    { id: "rose", label: "Crimson Rose", class: "bg-rose-500", hex: "#f43f5e" },
    { id: "sapphire", label: "Ocean Sapphire", class: "bg-blue-600", hex: "#2563eb" },
    { id: "sunset", label: "Solar Sunset", class: "bg-orange-600", hex: "#ea580c" },
    { id: "teal", label: "Lush Teal", class: "bg-teal-600", hex: "#0d9488" },
    { id: "fuchsia", label: "Fuchsia Magenta", class: "bg-fuchsia-600", hex: "#c026d3" },
    { id: "lime", label: "Forest Jade", class: "bg-lime-600", hex: "#65a30d" },
    { id: "slate", label: "Titanium Carbon", class: "bg-slate-600", hex: "#475569" },
];

export function Header() {
    const navigate = useNavigate();
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [themeMenuOpen, setThemeMenuOpen] = useState(false);
    const [accentMenuOpen, setAccentMenuOpen] = useState(false);

    const themeMenuRef = useRef<HTMLDivElement>(null);
    const accentMenuRef = useRef<HTMLDivElement>(null);

    const sidebarOpen = useUIStore((state) => state.sidebarOpen);
    const toggleSidebar = useUIStore((state) => state.toggleSidebar);
    const themeMode = useUIStore((state) => state.themeMode);
    const setThemeMode = useUIStore((state) => state.setThemeMode);
    const accentColor = useUIStore((state) => state.accentColor);
    const setAccentColor = useUIStore((state) => state.setAccentColor);

    const isSettingsPage = location.pathname === "/settings";

    const { data, isError } = useHealth();
    const backendOnline = !isError && data?.status === "running";

    const activeThemeObj = THEME_MODES.find((t) => t.id === themeMode) || THEME_MODES[0];
    const ActiveThemeIcon = activeThemeObj.icon;
    const activeAccentObj = ACCENT_COLORS.find((a) => a.id === accentColor) || ACCENT_COLORS[0];

    // Close dropdowns on outside click
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (themeMenuRef.current && !themeMenuRef.current.contains(e.target as Node)) {
                setThemeMenuOpen(false);
            }
            if (accentMenuRef.current && !accentMenuRef.current.contains(e.target as Node)) {
                setAccentMenuOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    return (
        <>
            <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 lg:px-6 dark:border-slate-800 dark:bg-slate-950 relative z-30">
                <div className="flex items-center gap-3">
                    {/* Mobile menu trigger */}
                    <Button
                        variant="ghost"
                        size="icon"
                        className="lg:hidden"
                        onClick={() => setMobileMenuOpen(true)}
                        aria-label="Open navigation"
                    >
                        <Menu className="h-5 w-5" />
                    </Button>

                    {/* Desktop sidebar toggle button */}
                    <Button
                        variant="ghost"
                        size="icon"
                        className="hidden lg:flex text-slate-500 hover:text-slate-900 dark:hover:text-white"
                        onClick={toggleSidebar}
                        title={sidebarOpen ? "Hide AI Platform Sidebar" : "Show AI Platform Sidebar"}
                        aria-label="Toggle AI Platform Sidebar"
                    >
                        {sidebarOpen ? (
                            <PanelLeftClose className="h-5 w-5" />
                        ) : (
                            <PanelLeftOpen className="h-5 w-5" />
                        )}
                    </Button>

                    <div className="flex h-10 w-10 items-center justify-center rounded-xl accent-bg shadow-sm cursor-pointer" onClick={() => navigate("/")}>
                        <Cpu className="h-5 w-5" />
                    </div>

                    <div className="cursor-pointer" onClick={() => navigate("/")}>
                        <h1 className="text-base font-bold leading-tight" style={{ color: "var(--foreground)" }}>
                            Anuj AI Lab
                        </h1>
                        <p className="hidden text-xs font-medium sm:block" style={{ color: "var(--text-muted)" }}>
                            Local AI Engineering Platform
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2 lg:gap-2.5">
                    <div className="hidden md:flex items-center gap-2">
                        <Badge
                            variant={backendOnline ? "default" : "destructive"}
                            className={backendOnline ? "bg-emerald-600 hover:bg-emerald-700" : ""}
                        >
                            Backend {backendOnline ? "Online" : "Offline"}
                        </Badge>

                        <Badge variant="outline" className="font-mono text-xs">
                            {data?.version ?? "v3.0.0"}
                        </Badge>
                    </div>

                    {/* 1. 12 Curated Theme Modes Selector (Replaces Inspector) */}
                    <div className="relative" ref={themeMenuRef}>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                                setThemeMenuOpen(!themeMenuOpen);
                                setAccentMenuOpen(false);
                            }}
                            className="h-8 text-xs font-semibold px-2.5 gap-1.5 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-primary"
                            title="12 Curated Theme Modes"
                        >
                            <ActiveThemeIcon className="h-3.5 w-3.5 accent-text" />
                            <span className="hidden sm:inline">{activeThemeObj.label}</span>
                            <ChevronDown className="h-3 w-3 opacity-60 ml-0.5" />
                        </Button>

                        {themeMenuOpen && (
                            <div className="absolute right-0 mt-2 w-72 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl p-2 z-50 animate-in fade-in-50 zoom-in-95 duration-100 max-h-[85vh] overflow-y-auto">
                                <div className="px-2.5 py-1.5 border-b border-slate-100 dark:border-slate-800 mb-1">
                                    <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-400">
                                        <Palette className="h-3.5 w-3.5 accent-text" /> 12 Theme Modes
                                    </div>
                                </div>
                                <div className="space-y-1">
                                    {THEME_MODES.map((t) => {
                                        const Icon = t.icon;
                                        const isSelected = themeMode === t.id;
                                        return (
                                            <button
                                                key={t.id}
                                                onClick={() => {
                                                    setThemeMode(t.id);
                                                    setThemeMenuOpen(false);
                                                }}
                                                className={`w-full flex items-center justify-between p-2 rounded-lg text-xs transition-colors text-left ${
                                                    isSelected
                                                        ? "accent-subtle font-semibold accent-text"
                                                        : "text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60"
                                                }`}
                                            >
                                                <div className="flex items-center gap-2.5 min-w-0">
                                                    <Icon className="h-4 w-4 shrink-0" />
                                                    <div className="truncate">
                                                        <p className="leading-tight">{t.label}</p>
                                                        <p className="text-[10px] text-slate-400 font-normal truncate">{t.desc}</p>
                                                    </div>
                                                </div>
                                                {isSelected && <Check className="h-3.5 w-3.5 shrink-0 accent-text ml-2" />}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* 2. 12 Dedicated Accent Color Palettes (Replaces Sun/Moon) */}
                    <div className="relative" ref={accentMenuRef}>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                                setAccentMenuOpen(!accentMenuOpen);
                                setThemeMenuOpen(false);
                            }}
                            className="h-8 text-xs font-semibold px-2.5 gap-1.5 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:text-primary"
                            title="12 Dedicated Accent Color Palettes"
                        >
                            <span
                                className="h-3.5 w-3.5 rounded-full shadow-sm ring-1 ring-white dark:ring-black"
                                style={{ backgroundColor: activeAccentObj.hex }}
                            />
                            <span className="hidden sm:inline">{activeAccentObj.label}</span>
                            <ChevronDown className="h-3 w-3 opacity-60 ml-0.5" />
                        </Button>

                        {accentMenuOpen && (
                            <div className="absolute right-0 mt-2 w-64 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xl p-3 z-50 animate-in fade-in-50 zoom-in-95 duration-100">
                                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2 mb-2">
                                    <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-slate-400">
                                        <Sparkles className="h-3.5 w-3.5 accent-text" /> 12 Accent Palettes
                                    </div>
                                    <span className="text-[10px] font-mono text-slate-400 font-semibold">{accentColor}</span>
                                </div>
                                <div className="grid grid-cols-2 gap-1.5">
                                    {ACCENT_COLORS.map((c) => {
                                        const isSelected = accentColor === c.id;
                                        return (
                                            <button
                                                key={c.id}
                                                onClick={() => {
                                                    setAccentColor(c.id);
                                                    setAccentMenuOpen(false);
                                                }}
                                                className={`flex items-center gap-2 p-1.5 rounded-lg text-xs transition-all ${
                                                    isSelected
                                                        ? "accent-subtle font-bold accent-text ring-1 ring-primary/40"
                                                        : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60"
                                                }`}
                                            >
                                                <span
                                                    className="h-3.5 w-3.5 rounded-full shrink-0 shadow-sm ring-1 ring-slate-200 dark:ring-slate-700"
                                                    style={{ backgroundColor: c.hex }}
                                                />
                                                <span className="truncate text-[11px]">{c.label}</span>
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* 3. Settings Quick Toggle (Instant Return to Chat if inside Settings) */}
                    {isSettingsPage ? (
                        <Button
                            variant="default"
                            size="sm"
                            onClick={() => navigate("/")}
                            className="h-8 text-xs font-semibold gap-1.5 accent-bg text-white shadow-sm"
                            title="Return instantly to AI Assistant"
                        >
                            <ArrowLeft className="h-3.5 w-3.5" />
                            <span>Back to Chat</span>
                        </Button>
                    ) : (
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => navigate("/settings")}
                            aria-label="Open settings"
                            className="h-8 w-8 text-slate-600 dark:text-slate-300 hover:text-primary"
                            title="Settings & Models"
                        >
                            <Settings className="h-4 w-4" />
                        </Button>
                    )}
                </div>
            </header>

            <MobileSidebar
                open={mobileMenuOpen}
                onOpenChange={setMobileMenuOpen}
            />
        </>
    );
}

export default Header;