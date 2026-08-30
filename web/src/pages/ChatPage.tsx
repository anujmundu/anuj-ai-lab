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
    Activity
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
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
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [isPending, setIsPending] = useState(false);
    const [sessions, setSessions] = useState<ChatSessionSummary[]>([]);
    const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [availableModels, setAvailableModels] = useState<string[]>([]);
    
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

    // Automatically hide AI Platform Engine sidebar when inside AI Assistant
    useEffect(() => {
        setGlobalSidebarOpen(false);
    }, [setGlobalSidebarOpen]);

    async function loadSessions() {
        try {
            const list = await chatSessionService.listSessions();
            setSessions(list);
            if (list.length > 0 && !activeSessionId) {
                loadSessionMessages(list[0].session_id);
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
        try {
            const detail = await chatSessionService.getSession(sessionId);
            const formatted: ChatMessage[] = detail.messages.map((m) => ({
                role: m.role,
                content: m.content,
                sources: m.sources,
            }));
            setMessages(formatted);
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
            setMessages((prev) => [
                ...prev,
                {
                    role: "assistant",
                    content: err.message || "An unexpected error occurred.",
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
                            <h1 className="text-lg sm:text-xl font-bold flex items-center gap-2 text-slate-900 dark:text-slate-100">
                                AI Assistant
                            </h1>
                            <p className="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 font-medium line-clamp-1 sm:line-clamp-none">
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
                        <EmptyChat />
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
        </section>
    );
}