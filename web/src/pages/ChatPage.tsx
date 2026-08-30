import { useState, useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { 
    MessageSquare, 
    Plus, 
    Trash2, 
    History, 
    PanelLeftClose, 
    PanelLeftOpen,
    Cpu,
    Pencil,
    Check,
    X,
    Layers,
    Activity,
    Key,
    Sparkles,
    ExternalLink,
    Zap,
    ShieldCheck
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
    ChatHistory,
    ChatInput,
    EmptyChat,
    LoadingMessage,
} from "@/components/chat";
import { chatSessionService, type ChatSessionSummary } from "@/services/chat_session.service";
import { modelsService } from "@/services/models.service";
import { queryKeys } from "@/lib/query-keys";
import { useUIStore } from "@/stores";
import type { ChatMessage } from "@/types";

export default function ChatPage() {
    const queryClient = useQueryClient();
    const [question, setQuestion] = useState("");
    const [isPending, setIsPending] = useState(false);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [availableModels, setAvailableModels] = useState<string[]>([]);
    
    // Cloud API Key State
    const [keyModalOpen, setKeyModalOpen] = useState(false);
    const [cloudApiKey, setCloudApiKey] = useState(() => localStorage.getItem("anuj_ai_cloud_api_key") || "");
    const [cloudProvider, setCloudProvider] = useState(() => localStorage.getItem("anuj_ai_cloud_provider") || "groq");
    const [showKey, setShowKey] = useState(false);

    // Persistent initial state from local storage
    const [sessions, setSessions] = useState<ChatSessionSummary[]>(() => {
        try {
            return JSON.parse(localStorage.getItem("anuj_ai_chat_sessions") || "[]");
        } catch {
            return [];
        }
    });

    const [activeSessionId, setActiveSessionId] = useState<string | null>(() => {
        return localStorage.getItem("anuj_ai_active_session_id") || null;
    });

    const [messages, setMessages] = useState<ChatMessage[]>(() => {
        try {
            const savedId = localStorage.getItem("anuj_ai_active_session_id");
            if (!savedId) return [];
            return JSON.parse(localStorage.getItem(`anuj_ai_messages_${savedId}`) || "[]");
        } catch {
            return [];
        }
    });
    
    // Inline rename state
    const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
    const [editingTitle, setEditingTitle] = useState("");
    const editInputRef = useRef<HTMLInputElement>(null);

    const selectedModel = useUIStore((state) => state.selectedModel);
    const setSelectedModel = useUIStore((state) => state.setSelectedModel);

    const globalSidebarOpen = useUIStore((state) => state.sidebarOpen);
    const setGlobalSidebarOpen = useUIStore((state) => state.setSidebarOpen);

    const inspectorOpen = useUIStore((state) => state.inspectorOpen);
    const toggleInspector = useUIStore((state) => state.toggleInspector);

    // Save active session & messages to local storage whenever they change
    useEffect(() => {
        if (activeSessionId) {
            localStorage.setItem("anuj_ai_active_session_id", activeSessionId);
            if (messages.length > 0) {
                localStorage.setItem(`anuj_ai_messages_${activeSessionId}`, JSON.stringify(messages));
            }
        }
    }, [messages, activeSessionId]);

    useEffect(() => {
        if (sessions.length > 0) {
            localStorage.setItem("anuj_ai_chat_sessions", JSON.stringify(sessions));
        }
    }, [sessions]);

    // Automatically hide AI Platform Engine sidebar when inside AI Assistant
    useEffect(() => {
        setGlobalSidebarOpen(false);
    }, [setGlobalSidebarOpen]);

    async function loadSessions() {
        try {
            const list = await chatSessionService.listSessions();
            if (list && list.length > 0) {
                setSessions(list);
                const currentId = activeSessionId || localStorage.getItem("anuj_ai_active_session_id");
                const targetSession = list.find((s) => s.session_id === currentId) || list[0];
                loadSessionMessages(targetSession.session_id);
            }
        } catch (err) {
            console.error("Failed to load sessions", err);
        }
    }

    async function loadModels() {
        try {
            const res = await modelsService.getAvailableModels();
            if (res && res.installed_models) {
                setAvailableModels(res.installed_models);
            }
        } catch {
            setAvailableModels(["qwen2.5:1.5b", "deepseek-r1:8b", "qwen2.5-coder:7b", "llama3.2:3b"]);
        }
    }

    async function loadSessionMessages(sessionId: string) {
        setActiveSessionId(sessionId);
        localStorage.setItem("anuj_ai_active_session_id", sessionId);

        // Preload from local cache immediately for 0ms visual latency
        try {
            const cached = localStorage.getItem(`anuj_ai_messages_${sessionId}`);
            if (cached) {
                setMessages(JSON.parse(cached));
            }
        } catch {
            // ignore
        }

        try {
            const detail = await chatSessionService.getSession(sessionId);
            const formatted: ChatMessage[] = detail.messages.map((m) => ({
                role: m.role,
                content: m.content,
                sources: m.sources,
            }));
            if (formatted.length > 0) {
                setMessages(formatted);
                localStorage.setItem(`anuj_ai_messages_${sessionId}`, JSON.stringify(formatted));
            }
        } catch (err) {
            console.error("Failed to load session messages", err);
        }
    }

    useEffect(() => {
        loadSessions();
        loadModels();
    }, []);

    // Multi-device real-time message sync (e.g. desktop + mobile opened side-by-side)
    useEffect(() => {
        if (!activeSessionId) return;

        const interval = setInterval(async () => {
            if (isPending) return;
            try {
                const detail = await chatSessionService.getSession(activeSessionId);
                const formatted: ChatMessage[] = detail.messages.map((m) => ({
                    role: m.role,
                    content: m.content,
                    sources: m.sources,
                }));
                setMessages((prev) => {
                    if (prev.length !== formatted.length) return formatted;
                    if (
                        prev.length > 0 &&
                        (prev[prev.length - 1].content !== formatted[formatted.length - 1].content ||
                         prev[prev.length - 1].role !== formatted[formatted.length - 1].role)
                    ) {
                        return formatted;
                    }
                    return prev;
                });
            } catch {
                // Silently ignore polling errors
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [activeSessionId, isPending]);

    // Multi-device session list sync
    useEffect(() => {
        const sessionInterval = setInterval(async () => {
            try {
                const list = await chatSessionService.listSessions();
                setSessions((prev) => {
                    if (prev.length !== list.length) return list;
                    return prev;
                });
            } catch {
                // Silently ignore
            }
        }, 5000);

        return () => clearInterval(sessionInterval);
    }, []);

    useEffect(() => {
        if (editingSessionId && editInputRef.current) {
            editInputRef.current.focus();
            editInputRef.current.select();
        }
    }, [editingSessionId]);

    async function handleCreateNewSession() {
        try {
            const newSession = await chatSessionService.createSession("New Conversation");
            setSessions([newSession, ...sessions]);
            setActiveSessionId(newSession.session_id);
            setMessages([]);
            toast.success("New conversation created.");
        } catch (err: any) {
            toast.error(err.message || "Failed to create session");
        }
    }

    function handleStartRename(sessionId: string, currentTitle: string, e: React.MouseEvent) {
        e.stopPropagation();
        setEditingSessionId(sessionId);
        setEditingTitle(currentTitle);
    }

    async function handleSaveRename(sessionId: string, e?: React.MouseEvent | React.FormEvent) {
        if (e) e.stopPropagation();
        const trimmed = editingTitle.trim();
        if (!trimmed) {
            setEditingSessionId(null);
            return;
        }

        try {
            await chatSessionService.renameSession(sessionId, trimmed);
            setSessions((prev) =>
                prev.map((s) => (s.session_id === sessionId ? { ...s, title: trimmed } : s))
            );
            toast.success("Conversation renamed.");
        } catch (err: any) {
            toast.error(err.message || "Failed to rename session");
        } finally {
            setEditingSessionId(null);
        }
    }

    function handleCancelRename(e: React.MouseEvent) {
        e.stopPropagation();
        setEditingSessionId(null);
    }

    async function handleDeleteSession(sessionId: string, e: React.MouseEvent) {
        e.stopPropagation();
        try {
            await chatSessionService.deleteSession(sessionId);
            const remaining = sessions.filter((s) => s.session_id !== sessionId);
            setSessions(remaining);
            if (activeSessionId === sessionId) {
                if (remaining.length > 0) {
                    loadSessionMessages(remaining[0].session_id);
                } else {
                    setActiveSessionId(null);
                    setMessages([]);
                }
            }
            toast.success("Conversation deleted.");
        } catch (err: any) {
            toast.error(err.message || "Failed to delete session");
        }
    }

    async function handleSendMessage() {
        const trimmed = question.trim();
        if (!trimmed || isPending) return;

        const userMsg: ChatMessage = { role: "user", content: trimmed };
        setMessages((prev) => [...prev, userMsg]);
        setQuestion("");
        setIsPending(true);

        try {
            let currentSessionId = activeSessionId;
            if (!currentSessionId) {
                const newSession = await chatSessionService.createSession(
                    trimmed.length > 40 ? trimmed.slice(0, 38) + "..." : trimmed
                );
                currentSessionId = newSession.session_id;
                setActiveSessionId(currentSessionId);
                setSessions([newSession, ...sessions]);
            }

            const res = await chatSessionService.sendMessage(currentSessionId, trimmed);
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: res.answer,
                    sources: res.sources,
                },
            ]);

            // Auto-rename session in list if updated by backend topic summary
            if (res.session_title) {
                setSessions((prev) =>
                    prev.map((s) =>
                        s.session_id === currentSessionId
                            ? { ...s, title: res.session_title! }
                            : s
                    )
                );
            }
        } catch (err: any) {
            const isNetworkError = err.message === "Network Error" || err.code === "ERR_NETWORK";
            const errorMsg = isNetworkError
                ? "Could not reach Anuj AI Lab API Gateway. Please check your internet connection or try again."
                : (err.message || "An unexpected error occurred.");
            toast.error(errorMsg);
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: `⚠️ **Connection Issue**: ${errorMsg}\n\n*If your Render free tier backend is spinning up from idle, please retry in 10-15 seconds.*`,
                },
            ]);
        } finally {
            setIsPending(false);
            queryClient.invalidateQueries({ queryKey: queryKeys.rag.diagnostics });
        }
    }

    return (
        <section className="flex flex-1 overflow-hidden h-full relative">
            {/* Conversation Threads Sidebar */}
            {sidebarOpen && (
                <>
                    {/* Backdrop for mobile */}
                    <div 
                        onClick={() => setSidebarOpen(false)} 
                        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-30 sm:hidden"
                    />
                    <div className="fixed inset-y-0 left-0 z-40 sm:relative sm:z-auto w-72 sm:w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 sm:bg-slate-50/50 sm:dark:bg-slate-900/50 p-4 flex flex-col gap-3 shrink-0 shadow-2xl sm:shadow-none transition-all">
                        <div className="flex items-center justify-between">
                            <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                                <History className="h-3.5 w-3.5" /> Sessions ({sessions.length})
                            </span>
                            <div className="flex items-center gap-1">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={handleCreateNewSession}
                                    className="h-7 text-xs bg-indigo-50 text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-950 dark:text-indigo-300 gap-1 px-2 font-medium"
                                >
                                    <Plus className="h-3 w-3" /> New Chat
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    onClick={() => setSidebarOpen(false)}
                                    className="h-7 w-7 sm:hidden text-slate-400"
                                    title="Close sidebar"
                                >
                                    <X className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>

                        <div className="flex-1 overflow-y-auto space-y-1.5">
                            {sessions.length === 0 ? (
                                <div className="text-center py-8 text-xs text-slate-400">
                                    <p>No saved threads.</p>
                                    <Button 
                                        onClick={handleCreateNewSession} 
                                        size="sm" 
                                        variant="outline" 
                                        className="mt-3 text-xs"
                                    >
                                        + Start Conversation
                                    </Button>
                                </div>
                            ) : (
                                sessions.map((s) => {
                                    const isSelected = activeSessionId === s.session_id;
                                    const isEditing = editingSessionId === s.session_id;

                                    return (
                                        <div
                                            key={s.session_id}
                                            onClick={() => {
                                                if (!isEditing) {
                                                    loadSessionMessages(s.session_id);
                                                    if (window.innerWidth < 640) setSidebarOpen(false);
                                                }
                                            }}
                                            className={`group flex items-center justify-between p-2.5 rounded-lg text-xs cursor-pointer transition-all ${
                                                isSelected
                                                    ? "bg-white dark:bg-slate-800 font-semibold text-indigo-600 dark:text-indigo-400 shadow-sm border border-slate-200 dark:border-slate-700"
                                                    : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/50"
                                            }`}
                                        >
                                            {isEditing ? (
                                                <form
                                                    onSubmit={(e) => {
                                                        e.preventDefault();
                                                        handleSaveRename(s.session_id, e);
                                                    }}
                                                    onClick={(e) => e.stopPropagation()}
                                                    className="flex items-center gap-1 w-full"
                                                >
                                                    <input
                                                        ref={editInputRef}
                                                        type="text"
                                                        value={editingTitle}
                                                        onChange={(e) => setEditingTitle(e.target.value)}
                                                        onKeyDown={(e) => {
                                                            if (e.key === "Escape") setEditingSessionId(null);
                                                        }}
                                                        className="w-full bg-slate-100 dark:bg-slate-900 border border-indigo-400 rounded px-1.5 py-0.5 text-xs text-slate-900 dark:text-white focus:outline-none"
                                                    />
                                                    <button
                                                        type="submit"
                                                        className="p-1 text-emerald-600 hover:text-emerald-700"
                                                        title="Save"
                                                    >
                                                        <Check className="h-3.5 w-3.5" />
                                                    </button>
                                                    <button
                                                        type="button"
                                                        onClick={handleCancelRename}
                                                        className="p-1 text-slate-400 hover:text-slate-600"
                                                        title="Cancel"
                                                    >
                                                        <X className="h-3.5 w-3.5" />
                                                    </button>
                                                </form>
                                            ) : (
                                                <>
                                                    <div className="flex items-center gap-2 truncate flex-1 mr-1">
                                                        <MessageSquare className="h-3.5 w-3.5 shrink-0" />
                                                        <span className="truncate">{s.title || "Conversation"}</span>
                                                    </div>
                                                    <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <button
                                                            onClick={(e) => handleStartRename(s.session_id, s.title, e)}
                                                            className="p-1 hover:text-indigo-600 text-slate-400"
                                                            title="Rename Chat"
                                                        >
                                                            <Pencil className="h-3 w-3" />
                                                        </button>
                                                        <button
                                                            onClick={(e) => handleDeleteSession(s.session_id, e)}
                                                            className="p-1 hover:text-red-600 text-slate-400"
                                                            title="Delete Session"
                                                        >
                                                            <Trash2 className="h-3 w-3" />
                                                        </button>
                                                    </div>
                                                </>
                                            )}
                                        </div>
                                    );
                                })
                            )}
                        </div>
                    </div>
                </>
            )}

            {/* Main Chat View */}
            <div className="flex flex-1 flex-col p-3 sm:p-6 gap-4 sm:gap-6 overflow-hidden w-full">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3 sm:pb-4">
                    <div className="flex items-center gap-3">
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className="h-8 w-8 text-slate-500"
                            title={sidebarOpen ? "Hide Sessions" : "Show Sessions"}
                        >
                            {sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelLeftOpen className="h-4 w-4" />}
                        </Button>
                        <div>
                            <h1 className="text-lg sm:text-xl font-bold flex items-center gap-2" style={{ color: "var(--foreground)" }}>
                                AI Assistant
                            </h1>
                            <p className="text-[11px] sm:text-xs font-medium line-clamp-1 sm:line-clamp-none" style={{ color: "var(--text-muted)" }}>
                                Multi-turn semantic conversations grounded in your ChromaDB knowledge base.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-2 flex-wrap">
                        {/* Toggle Sessions */}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className={`h-8 text-xs font-semibold gap-1.5 border-slate-200 dark:border-slate-800 ${
                                sidebarOpen
                                    ? "bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 border-indigo-300 dark:border-indigo-700"
                                    : "text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400"
                            }`}
                        >
                            <History className="h-3.5 w-3.5 text-indigo-500" />
                            <span className="hidden xs:inline sm:inline">{sidebarOpen ? "Hide Sessions" : "Show Sessions"}</span>
                            <span className="inline xs:hidden sm:hidden">Sessions</span>
                        </Button>

                        {/* Toggle AI Platform Engine */}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setGlobalSidebarOpen(!globalSidebarOpen)}
                            className={`h-8 text-xs font-semibold gap-1.5 border-slate-200 dark:border-slate-800 ${
                                globalSidebarOpen
                                    ? "bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 border-indigo-300 dark:border-indigo-700"
                                    : "text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400"
                            }`}
                        >
                            <Layers className="h-3.5 w-3.5 text-indigo-500" />
                            <span className="hidden sm:inline">{globalSidebarOpen ? "Hide AI Platform Engine" : "Show AI Platform Engine"}</span>
                            <span className="inline sm:hidden">Engine</span>
                        </Button>

                        {/* Toggle Execution Inspector */}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={toggleInspector}
                            className={`h-8 text-xs font-semibold gap-1.5 border-slate-200 dark:border-slate-800 ${
                                inspectorOpen
                                    ? "bg-indigo-50 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 border-indigo-300 dark:border-indigo-700"
                                    : "text-slate-700 dark:text-slate-300 hover:text-indigo-600 dark:hover:text-indigo-400"
                            }`}
                        >
                            <Activity className="h-3.5 w-3.5 text-indigo-500" />
                            <span>{inspectorOpen ? "Hide Inspector" : "Show Inspector"}</span>
                        </Button>

                        {/* Cloud LLM Engine Key Connection */}
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setKeyModalOpen(true)}
                            className={`h-8 text-xs font-semibold gap-1.5 border-slate-200 dark:border-slate-800 ${
                                cloudApiKey
                                    ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 border-emerald-300 dark:border-emerald-700"
                                    : "text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-950/30"
                            }`}
                        >
                            <Sparkles className="h-3.5 w-3.5 text-purple-500" />
                            <span>{cloudApiKey ? `⚡ ${cloudProvider === "groq" ? "Llama 3.3 70B" : cloudProvider.toUpperCase()} Active` : "⚡ Connect Free LLM"}</span>
                        </Button>

                        {/* Model Switcher Dropdown */}
                        <div className="flex items-center gap-1.5">
                            <Cpu className="h-4 w-4 text-indigo-500 hidden sm:inline" />
                            <select
                                value={selectedModel}
                                onChange={(e) => setSelectedModel(e.target.value)}
                                className="text-xs font-mono font-semibold bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2 py-1.5 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer max-w-[140px] sm:max-w-none truncate"
                            >
                                <option value="auto">✨ Auto Router</option>
                                {availableModels.map((m) => (
                                    <option key={m} value={m}>{m}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                <div className="flex flex-1 flex-col gap-4 sm:gap-6 overflow-y-auto w-full max-w-5xl 2xl:max-w-6xl mx-auto">
                    {messages.length === 0 ? (
                        <EmptyChat
                            onConnectLLM={() => setKeyModalOpen(true)}
                            onSelectPrompt={(text) => setQuestion(text)}
                        />
                    ) : (
                        <ChatHistory messages={messages} />
                    )}

                    {isPending && <LoadingMessage />}
                </div>

                <div className="w-full max-w-5xl 2xl:max-w-6xl mx-auto">
                    <ChatInput
                        value={question}
                        onChange={setQuestion}
                        onSubmit={handleSendMessage}
                        disabled={isPending}
                    />
                </div>
            </div>

            {/* Cloud LLM Engine Key Connection Modal */}
            {keyModalOpen && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-5 animate-in fade-in zoom-in duration-150">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                                <div className="p-2 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
                                    <Sparkles className="h-5 w-5" />
                                </div>
                                <div>
                                    <h3 className="font-bold text-base text-slate-900 dark:text-white">
                                        Connect Cloud LLM Engine
                                    </h3>
                                    <p className="text-xs text-slate-500 dark:text-slate-400">
                                        Unlock 100% boundless, ChatGPT/Gemini-grade answers for all questions.
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => setKeyModalOpen(false)}
                                className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1 rounded-lg"
                            >
                                <X className="h-5 w-5" />
                            </button>
                        </div>

                        <div className="space-y-4 text-xs">
                            <div className="space-y-1.5">
                                <label className="font-semibold text-slate-700 dark:text-slate-300">
                                    Select Neural LLM Provider:
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
                                            className="text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-1 font-medium text-[11px]"
                                        >
                                            Get Free Groq Key (10s) <ExternalLink className="h-3 w-3" />
                                        </a>
                                    )}
                                    {cloudProvider === "gemini" && (
                                        <a
                                            href="https://aistudio.google.com/app/apikey"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-purple-600 dark:text-purple-400 hover:underline flex items-center gap-1 font-medium text-[11px]"
                                        >
                                            Get Free Gemini Key <ExternalLink className="h-3 w-3" />
                                        </a>
                                    )}
                                </div>
                                <div className="relative">
                                    <Input
                                        type={showKey ? "text" : "password"}
                                        value={cloudApiKey}
                                        onChange={(e) => setCloudApiKey(e.target.value)}
                                        placeholder={
                                            cloudProvider === "groq"
                                                ? "Paste gsk_..."
                                                : cloudProvider === "gemini"
                                                ? "Paste AIzaSy..."
                                                : "Paste your API key..."
                                        }
                                        className="font-mono text-xs pr-16 bg-slate-50 dark:bg-slate-800"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowKey(!showKey)}
                                        className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 font-medium px-1.5 py-0.5 rounded"
                                    >
                                        {showKey ? "Hide" : "Show"}
                                    </button>
                                </div>
                                <p className="text-[11px] text-slate-400">
                                    Saved securely in your browser's LocalStorage and sent via encrypted HTTPS.
                                </p>
                            </div>
                        </div>

                        <div className="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800">
                            {cloudApiKey ? (
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => {
                                        setCloudApiKey("");
                                        localStorage.removeItem("anuj_ai_cloud_api_key");
                                        localStorage.removeItem("anuj_ai_cloud_provider");
                                        toast.info("Cloud API key cleared.");
                                    }}
                                    className="text-xs text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
                                >
                                    Disconnect Key
                                </Button>
                            ) : <div />}

                            <div className="flex items-center gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setKeyModalOpen(false)}
                                    className="text-xs"
                                >
                                    Cancel
                                </Button>
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
                                        setKeyModalOpen(false);
                                    }}
                                    className="text-xs bg-purple-600 hover:bg-purple-700 text-white font-medium"
                                >
                                    Save & Activate
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
}