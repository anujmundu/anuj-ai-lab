import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { 
    Cpu, 
    Palette, 
    Activity, 
    Sparkles, 
    Check, 
    Moon, 
    Sun, 
    Monitor,
    Layers,
    Code,
    Brain,
    Eye,
    Zap,
    Trees,
    Coffee,
    Waves,
    Flame,
    Sunset,
    BookOpen,
    Snowflake,
    Gem,
    Plus,
    ArrowLeft
} from "lucide-react";
import { Button } from "@/components/ui/button";

import { useHealth } from "@/hooks/system/useHealth";
import { modelsService, type AvailableModelsResponse } from "@/services/models.service";
import { useUIStore, type AccentColor, type ThemeMode } from "@/stores";

import { Badge } from "@/components/ui/badge";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

const THEME_MODES: { id: ThemeMode; label: string; desc: string; icon: any }[] = [
    { id: "light", label: "Pure Light", desc: "Crisp daylight with slate contrast", icon: Sun },
    { id: "dark", label: "Midnight Obsidian", desc: "Deep dark with sleek borders", icon: Moon },
    { id: "cyberpunk", label: "Cyberpunk Void", desc: "Ultra-dark with glowing accents", icon: Sparkles },
    { id: "forest", label: "Nordic Forest", desc: "Organic emerald & deep spruce", icon: Trees },
    { id: "espresso", label: "Velvet Espresso", desc: "Warm mocha & rich roasted tones", icon: Coffee },
    { id: "ocean", label: "Ocean Depths", desc: "Nautical abyss & deep navy", icon: Waves },
    { id: "amethyst", label: "Royal Amethyst", desc: "Regal dark violet & dusk purple", icon: Gem },
    { id: "crimson", label: "Crimson Eclipse", desc: "Bold blood-moon & dark charcoal", icon: Flame },
    { id: "sunset_glow", label: "Sunset Dusk", desc: "Warm amber dusk & golden shadows", icon: Sunset },
    { id: "sepia", label: "Vintage Sepia", desc: "Soft warm antique book parchment", icon: BookOpen },
    { id: "arctic", label: "Arctic Frost", desc: "Cool glacier ice & polar slate", icon: Snowflake },
    { id: "system", label: "System Adaptive", desc: "Synchronizes with device OS time", icon: Monitor },
];

const ACCENT_COLORS: { id: AccentColor; label: string; class: string }[] = [
    { id: "indigo", label: "Electric Indigo", class: "bg-indigo-600" },
    { id: "emerald", label: "Vibrant Emerald", class: "bg-emerald-600" },
    { id: "cyan", label: "Neon Cyan", class: "bg-cyan-500" },
    { id: "violet", label: "Deep Violet", class: "bg-purple-600" },
    { id: "amber", label: "Amber Gold", class: "bg-amber-500" },
    { id: "rose", label: "Crimson Rose", class: "bg-rose-500" },
    { id: "sapphire", label: "Ocean Sapphire", class: "bg-blue-600" },
    { id: "sunset", label: "Solar Sunset", class: "bg-orange-600" },
    { id: "teal", label: "Lush Teal", class: "bg-teal-600" },
    { id: "fuchsia", label: "Fuchsia Magenta", class: "bg-fuchsia-600" },
    { id: "lime", label: "Forest Jade", class: "bg-lime-600" },
    { id: "slate", label: "Titanium Carbon", class: "bg-slate-600" },
];

const TIER_ICONS: Record<string, any> = {
    fast_intent: Zap,
    code_execution: Code,
    deep_reasoning: Brain,
    vision_ocr: Eye,
    general_chat: Layers,
};

export default function SettingsPage() {
    const navigate = useNavigate();
    const themeMode = useUIStore((state) => state.themeMode);
    const setThemeMode = useUIStore((state) => state.setThemeMode);

    const accentColor = useUIStore((state) => state.accentColor);
    const setAccentColor = useUIStore((state) => state.setAccentColor);

    const {
        data,
        isError,
    } = useHealth();

    const [modelsData, setModelsData] = useState<AvailableModelsResponse | null>(null);
    const [activeAddTier, setActiveAddTier] = useState<string | null>(null);

    useEffect(() => {
        modelsService.getAvailableModels()
            .then((res) => {
                if (res) {
                    setModelsData(res);
                }
            })
            .catch((err) => {
                console.warn("Could not fetch models", err);
            });
    }, []);

    const handleSetPrimary = async (tierKey: string, modelName: string) => {
        // Optimistic UI update
        if (modelsData?.preferred_tiers) {
            const current = modelsData.preferred_tiers[tierKey];
            const currentList = Array.isArray(current) ? current : current ? [current] : [];
            const updatedList = [modelName, ...currentList.filter((m) => m !== modelName)];
            setModelsData({
                ...modelsData,
                preferred_tiers: {
                    ...modelsData.preferred_tiers,
                    [tierKey]: updatedList,
                },
            });
        }

        try {
            await modelsService.setPrimaryModel(tierKey, modelName);
            toast.success(`⭐ Set ${modelName} as Primary for ${tierKey.replace(/_/g, " ")}`);
            setActiveAddTier(null);
        } catch (err) {
            console.error("Failed to update tier", err);
            toast.error("Failed to update primary model tier");
            modelsService.getAvailableModels().then(setModelsData);
        }
    };

    const backendOnline =
        !isError &&
        data?.status === "running";

    const tiers = modelsData?.preferred_tiers || modelsData?.tier_mapping || {};
    const installedModels = modelsData?.installed_models || [];

    // Cloud LLM Key State
    const [cloudApiKey, setCloudApiKey] = useState(() => localStorage.getItem("anuj_ai_cloud_api_key") || "");
    const [cloudProvider, setCloudProvider] = useState(() => localStorage.getItem("anuj_ai_cloud_provider") || "groq");
    const [showKey, setShowKey] = useState(false);

    return (
        <section className="flex flex-1 flex-col gap-6 p-6 overflow-y-auto w-full">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
                        Settings & Model Engines
                    </h1>

                    <p className="mt-1 text-xs text-muted-foreground">
                        Connect cloud neural LLMs (Groq Llama 3.3 70B, Google Gemini, OpenAI), customize 12 workspace theme modes, and inspect your Ollama fleet.
                    </p>
                </div>

                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate("/")}
                    className="h-9 font-semibold text-xs gap-2 border-slate-200 dark:border-slate-800 hover:border-primary text-slate-700 dark:text-slate-300 shadow-sm shrink-0"
                >
                    <ArrowLeft className="h-3.5 w-3.5 text-primary" />
                    <span>Back to AI Assistant</span>
                </Button>
            </div>

            {/* Cloud Neural LLM Engine Settings Card */}
            <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <div>
                            <CardTitle className="flex items-center gap-2 text-base text-slate-900 dark:text-white">
                                <Sparkles className="h-4 w-4 text-purple-500" /> Cloud LLM Engine & API Keys
                            </CardTitle>
                            <CardDescription className="text-xs">
                                Connect high-speed cloud neural networks for unlimited, ChatGPT/Gemini-grade answers across any subject.
                            </CardDescription>
                        </div>
                        {cloudApiKey ? (
                            <Badge className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20 text-xs">
                                ⚡ {cloudProvider.toUpperCase()} Connected
                            </Badge>
                        ) : (
                            <Badge variant="outline" className="text-xs text-slate-400">
                                Offline / Local Only
                            </Badge>
                        )}
                    </div>
                </CardHeader>
                <CardContent className="space-y-4 text-xs">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                            <label className="font-semibold text-slate-700 dark:text-slate-300">
                                Select LLM Provider:
                            </label>
                            <select
                                value={cloudProvider}
                                onChange={(e) => setCloudProvider(e.target.value)}
                                className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 font-medium text-slate-900 dark:text-white cursor-pointer focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                                <option value="groq">⚡ Groq — Meta Llama 3.3 70B (Free, 500 tokens/sec - Recommended)</option>
                                <option value="gemini">✨ Google Gemini — Gemini 1.5 Flash (Free Tier)</option>
                                <option value="openai">🧠 OpenAI — GPT-4o / GPT-4o-mini</option>
                                <option value="openrouter">🌐 OpenRouter — Multi-Model Open Source Fleet</option>
                            </select>
                        </div>

                        <div className="space-y-1.5">
                            <div className="flex items-center justify-between">
                                <label className="font-semibold text-slate-700 dark:text-slate-300">
                                    API Key:
                                </label>
                                {cloudProvider === "groq" && (
                                    <a
                                        href="https://console.groq.com/keys"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-purple-600 dark:text-purple-400 hover:underline text-[11px] font-medium"
                                    >
                                        Get Free Groq Key (10s) ↗
                                    </a>
                                )}
                                {cloudProvider === "gemini" && (
                                    <a
                                        href="https://aistudio.google.com/app/apikey"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-purple-600 dark:text-purple-400 hover:underline text-[11px] font-medium"
                                    >
                                        Get Free Gemini Key ↗
                                    </a>
                                )}
                            </div>
                            <div className="relative">
                                <input
                                    type={showKey ? "text" : "password"}
                                    value={cloudApiKey}
                                    onChange={(e) => setCloudApiKey(e.target.value)}
                                    placeholder={
                                        cloudProvider === "groq"
                                            ? "Paste gsk_..."
                                            : cloudProvider === "gemini"
                                            ? "Paste AIzaSy..."
                                            : "Paste API key..."
                                    }
                                    className="w-full font-mono text-xs pr-16 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2.5 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowKey(!showKey)}
                                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 font-medium px-1.5 py-0.5 rounded"
                                >
                                    {showKey ? "Hide" : "Show"}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800">
                        <p className="text-[11px] text-slate-400">
                            Keys are stored locally in your browser and sent securely over encrypted HTTPS.
                        </p>

                        <div className="flex items-center gap-2">
                            {cloudApiKey && (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        setCloudApiKey("");
                                        localStorage.removeItem("anuj_ai_cloud_api_key");
                                        localStorage.removeItem("anuj_ai_cloud_provider");
                                        toast.info("Cloud API key disconnected.");
                                    }}
                                    className="text-xs text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
                                >
                                    Disconnect
                                </Button>
                            )}
                            <Button
                                size="sm"
                                onClick={() => {
                                    const trimmed = cloudApiKey.trim();
                                    if (trimmed) {
                                        localStorage.setItem("anuj_ai_cloud_api_key", trimmed);
                                        localStorage.setItem("anuj_ai_cloud_provider", cloudProvider);
                                        toast.success(`Connected to ${cloudProvider.toUpperCase()} Cloud LLM!`);
                                    } else {
                                        localStorage.removeItem("anuj_ai_cloud_api_key");
                                        localStorage.removeItem("anuj_ai_cloud_provider");
                                    }
                                }}
                                className="text-xs bg-purple-600 hover:bg-purple-700 text-white font-medium px-4"
                            >
                                Save Key & Activate
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <div className="grid gap-6 lg:grid-cols-2">
                {/* 12 Theme Modes */}
                <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm lg:col-span-2">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle className="flex items-center gap-2 text-base">
                                    <Palette className="h-4 w-4 accent-text" /> 12 Curated Theme Modes
                                </CardTitle>
                                <CardDescription className="text-xs">
                                    Select from daylight, dark obsidian, organic earth, and specialty ambient palettes.
                                </CardDescription>
                            </div>
                            <Badge variant="outline" className="font-mono text-xs uppercase">
                                Active: {themeMode.replace("_", " ")}
                            </Badge>
                        </div>
                    </CardHeader>

                    <CardContent>
                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6 gap-2.5">
                            {THEME_MODES.map((t) => {
                                const Icon = t.icon;
                                const isActive = themeMode === t.id;
                                return (
                                    <button
                                        key={t.id}
                                        onClick={() => setThemeMode(t.id)}
                                        className={`flex flex-col items-start p-3 rounded-xl border text-left transition-all relative ${
                                            isActive
                                                ? "accent-border accent-subtle ring-1 ring-primary shadow-sm"
                                                : "border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-700"
                                        }`}
                                    >
                                        <div className="flex items-center justify-between w-full mb-1">
                                            <div className="flex items-center gap-2">
                                                <Icon className="h-4 w-4 shrink-0" />
                                                <span className="text-xs font-bold">{t.label}</span>
                                            </div>
                                            {isActive && (
                                                <span className="h-2 w-2 rounded-full accent-bg" />
                                            )}
                                        </div>
                                        <span className="text-[10px] text-slate-400 leading-tight">
                                            {t.desc}
                                        </span>
                                    </button>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>

                {/* 12 Accent Colors */}
                <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm lg:col-span-2">
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <div>
                                <CardTitle className="flex items-center gap-2 text-base">
                                    <Sparkles className="h-4 w-4 accent-text" /> 12 Dedicated Accent Color Palettes
                                </CardTitle>
                                <CardDescription className="text-xs">
                                    Controls primary highlights, navigation badges, glowing indicators, and focus states.
                                </CardDescription>
                            </div>
                            <Badge variant="outline" className="font-mono text-xs uppercase">
                                Active Accent: {accentColor}
                            </Badge>
                        </div>
                    </CardHeader>

                    <CardContent>
                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 2xl:grid-cols-12 gap-2.5">
                            {ACCENT_COLORS.map((c) => {
                                const isActive = accentColor === c.id;
                                return (
                                    <button
                                        key={c.id}
                                        onClick={() => setAccentColor(c.id)}
                                        className={`flex items-center gap-2.5 p-2.5 rounded-xl border text-xs font-semibold transition-all ${
                                            isActive
                                                ? "border-slate-900 dark:border-white bg-slate-100 dark:bg-slate-800 shadow-sm"
                                                : "border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 hover:border-slate-300 dark:hover:border-slate-700"
                                        }`}
                                    >
                                        <span className={`h-4 w-4 rounded-full ${c.class} shrink-0 flex items-center justify-center shadow-xs`}>
                                            {isActive && <Check className="h-2.5 w-2.5 text-white" />}
                                        </span>
                                        <span className="truncate text-slate-800 dark:text-slate-200">{c.label}</span>
                                    </button>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>

                {/* Backend & Gateway Status */}
                <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between">
                    <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center gap-2 text-base">
                                <Activity className="h-4 w-4 text-emerald-500" /> Backend & API Gateway
                            </CardTitle>
                            <Badge
                                variant={backendOnline ? "default" : "destructive"}
                                className={backendOnline ? "bg-emerald-600 hover:bg-emerald-700 text-xs" : "text-xs"}
                            >
                                {backendOnline ? "Online (Running)" : "Offline"}
                            </Badge>
                        </div>
                        <CardDescription className="text-xs">
                            FastAPI real-time telemetry parameters.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-3 pt-0">
                        <div className="flex items-center justify-between text-xs py-1">
                            <span className="font-medium text-slate-600 dark:text-slate-400">Release Version</span>
                            <Badge variant="outline" className="font-mono text-xs">
                                {data?.version ?? "v3.0.0"}
                            </Badge>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between text-xs py-1">
                            <span className="font-medium text-slate-600 dark:text-slate-400">Base Gateway URL</span>
                            <code className="rounded bg-slate-100 dark:bg-slate-800 px-2 py-0.5 font-mono text-[11px] accent-text font-bold">
                                http://127.0.0.1:8000
                            </code>
                        </div>

                        <Separator />

                        <div className="flex items-center justify-between text-xs py-1">
                            <span className="font-medium text-slate-600 dark:text-slate-400">Vector Storage Engine</span>
                            <span className="font-mono text-slate-500 text-xs">ChromaDB Persistent (vector_db/)</span>
                        </div>
                    </CardContent>
                </Card>

                {/* Local Model Fleet & Dynamic Router */}
                <Card className="border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col justify-between">
                    <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center gap-2 text-base">
                                <Cpu className="h-4 w-4 accent-text" /> Installed Model Fleet
                            </CardTitle>
                            <Badge variant="outline" className="font-mono text-xs">
                                {installedModels.length} Models Detected
                            </Badge>
                        </div>
                        <CardDescription className="text-xs">
                            Active Ollama LLM instances available for local execution.
                        </CardDescription>
                    </CardHeader>

                    <CardContent className="space-y-3 pt-0">
                        <div className="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto pr-1">
                            {installedModels.length > 0 ? (
                                installedModels.map((m) => (
                                    <Badge 
                                        key={m} 
                                        variant="secondary" 
                                        className="font-mono text-xs py-1 px-2.5 bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700"
                                    >
                                        🤖 {m}
                                    </Badge>
                                ))
                            ) : (
                                <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/50 text-xs text-slate-500 font-mono">
                                    Defaulting: qwen2.5:1.5b, deepseek-r1:8b, qwen2.5-coder:7b, llama3.2:3b
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Routing Tiers */}
                <Card className="lg:col-span-2 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
                    <CardHeader>
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                            <div>
                                <CardTitle className="flex items-center gap-2 text-base">
                                    <Layers className="h-4 w-4 accent-text" /> Dynamic Task Routing Tiers
                                </CardTitle>
                                <CardDescription className="text-xs mt-0.5">
                                    Click any model badge to set it as the <strong className="text-indigo-600 dark:text-indigo-400">★ Primary</strong> model for that workload in 1-click.
                                </CardDescription>
                            </div>
                            <Badge variant="outline" className="font-mono text-xs w-fit">
                                1-Click Priority Active
                            </Badge>
                        </div>
                    </CardHeader>

                    <CardContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            {Object.entries(tiers).map(([tierKey, modelVal]) => {
                                const Icon = TIER_ICONS[tierKey] || Sparkles;
                                const modelList = Array.isArray(modelVal) ? modelVal : [modelVal];
                                const primaryModel = modelList[0];
                                const fallbackModels = modelList.slice(1);
                                const otherInstalled = installedModels.filter((m) => !modelList.includes(m));
                                const isAdding = activeAddTier === tierKey;

                                return (
                                    <div 
                                        key={tierKey} 
                                        className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/70 dark:bg-slate-950/70 flex flex-col justify-between space-y-3.5 hover:border-slate-300 dark:hover:border-slate-700 transition-all shadow-2xs h-full"
                                    >
                                        {/* Tier Header */}
                                        <div className="flex items-center justify-between pb-1 border-b border-slate-200/60 dark:border-slate-800/60">
                                            <div className="flex items-center gap-2 text-xs font-bold accent-text uppercase tracking-wider">
                                                <Icon className="h-4 w-4 shrink-0" />
                                                <span>{tierKey.replace(/_/g, " ")}</span>
                                            </div>
                                            <Badge variant="outline" className="text-[10px] uppercase font-bold py-0 h-4">
                                                {modelList.length} Models
                                            </Badge>
                                        </div>

                                        {/* Primary Model Display */}
                                        <div className="space-y-1">
                                            <span className="text-[10px] text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider flex items-center gap-1">
                                                <span>★ Primary Model:</span>
                                            </span>
                                            <div className="flex items-center justify-between p-2 rounded-lg bg-indigo-600 dark:bg-indigo-500 text-white font-mono text-xs font-bold shadow-xs">
                                                <div className="flex items-center gap-2 truncate">
                                                    <span className="text-amber-300">★</span>
                                                    <span className="truncate">{primaryModel}</span>
                                                </div>
                                                <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-black/20 text-white font-sans font-semibold shrink-0">
                                                    Active
                                                </span>
                                            </div>
                                        </div>

                                        {/* Fallback Priority Models */}
                                        <div className="space-y-1.5 flex-1">
                                            <span className="text-[10px] text-slate-500 dark:text-slate-400 font-semibold uppercase tracking-wider">
                                                Fallback Priority (Click to Promote):
                                            </span>
                                            <div className="flex flex-wrap gap-1.5">
                                                {fallbackModels.map((m) => (
                                                    <button
                                                        key={m}
                                                        onClick={() => handleSetPrimary(tierKey, m)}
                                                        title={`Click to promote ${m} to ★ Primary`}
                                                        className="text-[11px] font-mono px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:border-indigo-400 dark:hover:border-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50/50 dark:hover:bg-indigo-950/30 transition-all flex items-center gap-1 cursor-pointer shadow-2xs"
                                                    >
                                                        <span className="text-slate-400">↳</span>
                                                        <span>{m}</span>
                                                    </button>
                                                ))}

                                                {/* More Models Button */}
                                                {otherInstalled.length > 0 && (
                                                    <button
                                                        onClick={() => setActiveAddTier(isAdding ? null : tierKey)}
                                                        title="Browse other installed models"
                                                        className="text-[11px] font-mono px-2 py-1 rounded-lg border border-dashed border-slate-300 dark:border-slate-700 text-slate-500 hover:text-indigo-600 hover:border-indigo-400 flex items-center gap-1 transition-colors cursor-pointer"
                                                    >
                                                        <Plus className="h-3 w-3" />
                                                        <span>{isAdding ? "Close" : "More"}</span>
                                                    </button>
                                                )}
                                            </div>
                                        </div>

                                        {/* Quick Pick Drawer */}
                                        {isAdding && otherInstalled.length > 0 && (
                                            <div className="p-2.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-1.5 animate-in fade-in duration-200">
                                                <div className="text-[10px] text-slate-500 font-semibold uppercase">
                                                    Click to promote to ★ Primary:
                                                </div>
                                                <div className="flex flex-wrap gap-1 max-h-24 overflow-y-auto pr-1">
                                                    {otherInstalled.map((m) => (
                                                        <button
                                                            key={m}
                                                            onClick={() => handleSetPrimary(tierKey, m)}
                                                            className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-indigo-50 dark:hover:bg-indigo-950/40 hover:text-indigo-600 hover:border-indigo-400 transition-colors cursor-pointer"
                                                        >
                                                            + {m}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </CardContent>
                </Card>
            </div>
        </section>
    );
}