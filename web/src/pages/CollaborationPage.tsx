import { useState, useEffect } from "react";
import { 
    Users, 
    CheckCircle2, 
    XCircle, 
    Sparkles, 
    ShieldAlert, 
    Search, 
    Code, 
    Eye, 
    Layers, 
    RefreshCw,
    Send
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { collaborationService, type CollaborationSession } from "@/services/collaboration.service";

export default function CollaborationPage() {
    const [goal, setGoal] = useState("Implement and review a secure token rate limiter algorithm.");
    const [sessions, setSessions] = useState<CollaborationSession[]>([]);
    const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const [loading, setLoading] = useState(true);

    const selectedSession = sessions.find((s) => s.session_id === selectedSessionId) || (sessions.length > 0 ? sessions[0] : null);

    async function loadSessions() {
        try {
            const data = await collaborationService.listSessions();
            setSessions(data);
            setSelectedSessionId((currentId) => {
                if (currentId && data.some((s) => s.session_id === currentId)) {
                    return currentId;
                }
                return data.length > 0 ? data[0].session_id : null;
            });
        } catch (err) {
            console.error("Failed to load collaboration sessions", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadSessions();
        const interval = setInterval(loadSessions, 3000);
        return () => clearInterval(interval);
    }, []);

    async function handleStartCollaboration() {
        if (!goal.trim()) return;
        setSubmitting(true);
        try {
            const res = await collaborationService.createSession(goal);
            setSelectedSessionId(res.session_id);
            await loadSessions();
        } catch (err: any) {
            alert(err.message || "Failed to start collaboration");
        } finally {
            setSubmitting(false);
        }
    }

    async function handleDecision(approved: boolean) {
        if (!selectedSession) return;
        try {
            await collaborationService.approveAction(selectedSession.session_id, approved);
            await loadSessions();
        } catch (err: any) {
            alert(err.message || "Approval decision failed");
        }
    }

    function getRoleBadge(role: string) {
        switch (role) {
            case "researcher":
                return <Badge variant="secondary" className="bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 gap-1"><Search className="h-3 w-3" /> Researcher</Badge>;
            case "coder":
                return <Badge variant="secondary" className="bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 gap-1"><Code className="h-3 w-3" /> Coder</Badge>;
            case "critic":
                return <Badge variant="secondary" className="bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 gap-1"><Eye className="h-3 w-3" /> Critic (DeepSeek-R1)</Badge>;
            case "orchestrator":
                return <Badge variant="secondary" className="bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 gap-1"><Layers className="h-3 w-3" /> Orchestrator</Badge>;
            default:
                return <Badge variant="outline" className="text-xs uppercase">{role}</Badge>;
        }
    }

    return (
        <section className="flex flex-1 flex-col gap-6 p-6 overflow-y-auto w-full">
            {/* Header */}
            <div>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-md">
                            <Users className="h-5 w-5" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                                Multi-Agent Collaboration & Deliberation
                            </h1>
                            <p className="text-slate-500 dark:text-slate-400 text-sm">
                                4-Role collaborative debate across Researcher, Coder, Critic, and Orchestrator with Human-in-the-Loop (HITL) gates.
                            </p>
                        </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={loadSessions} className="flex items-center gap-1.5 text-xs">
                        <RefreshCw className="h-3.5 w-3.5" /> Refresh
                    </Button>
                </div>
            </div>

            {/* Launch Box */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm space-y-4">
                <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-blue-500" />
                    <span className="font-semibold text-sm text-slate-900 dark:text-white">Initiate 4-Agent Debate Session</span>
                </div>
                <div className="flex flex-col sm:flex-row gap-3">
                    <Input 
                        value={goal}
                        onChange={(e) => setGoal(e.target.value)}
                        placeholder="Define multi-agent problem (e.g. 'Synthesize a distributed consensus algorithm with security review')..."
                        className="text-xs flex-1"
                    />
                    <Button 
                        onClick={handleStartCollaboration}
                        disabled={submitting || !goal.trim()}
                        className="bg-blue-600 hover:bg-blue-700 text-white text-xs whitespace-nowrap gap-1.5"
                    >
                        <Send className="h-3.5 w-3.5" /> {submitting ? "Initiating Debate..." : "Start Collaboration"}
                    </Button>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Session List Sidebar */}
                <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 shadow-sm space-y-3">
                    <span className="text-xs font-bold uppercase tracking-wide text-slate-400 block mb-2">
                        Deliberation Sessions ({sessions.length})
                    </span>

                    {loading ? (
                        <div className="py-8 text-center text-xs text-slate-400">Loading sessions...</div>
                    ) : sessions.length === 0 ? (
                        <div className="py-8 text-center text-xs text-slate-400">No collaboration sessions yet. Launch your first session above!</div>
                    ) : (
                        <div className="space-y-2 max-h-[600px] overflow-y-auto">
                            {sessions.map((s) => {
                                const isSelected = selectedSession?.session_id === s.session_id;
                                const timestamp = typeof s.created_at === "number" ? s.created_at * 1000 : Date.parse(s.created_at);
                                return (
                                    <div 
                                        key={s.session_id}
                                        onClick={() => setSelectedSessionId(s.session_id)}
                                        className={`p-3 rounded-lg border transition-all cursor-pointer ${
                                            isSelected 
                                                ? "border-blue-500 bg-blue-50/40 dark:bg-blue-950/20 shadow-sm ring-1 ring-blue-500" 
                                                : "border-slate-100 dark:border-slate-800 hover:border-slate-300"
                                        }`}
                                    >
                                        <div className="flex items-center justify-between gap-2 mb-1">
                                            <Badge 
                                                variant={
                                                    s.status === "completed" ? "default" :
                                                    s.status === "awaiting_approval" ? "destructive" : "secondary"
                                                }
                                                className="text-[10px] uppercase font-bold"
                                            >
                                                {s.status.replace("_", " ")}
                                            </Badge>
                                            <span className="text-[10px] text-slate-400 font-mono">
                                                {isNaN(timestamp) ? "" : new Date(timestamp).toLocaleTimeString()}
                                            </span>
                                        </div>
                                        <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 line-clamp-2">
                                            {s.goal}
                                        </p>
                                        <div className="mt-2 text-[10px] text-slate-400 flex items-center justify-between">
                                            <span>{s.messages?.length || 0} Dialogue turns</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Live Shared Blackboard & HITL Review */}
                <div className="lg:col-span-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-6">
                    {selectedSession ? (
                        <>
                            <div className="border-b border-slate-100 dark:border-slate-800 pb-4">
                                <div className="flex items-center justify-between">
                                    <Badge variant="outline" className="font-mono text-xs text-blue-600 dark:text-blue-400 border-blue-200">
                                        Session: {selectedSession.session_id}
                                    </Badge>
                                    <Badge 
                                        variant={
                                            selectedSession.status === "completed" ? "default" :
                                            selectedSession.status === "awaiting_approval" ? "destructive" : "secondary"
                                        }
                                        className="text-xs font-semibold"
                                    >
                                        {selectedSession.status.toUpperCase().replace("_", " ")}
                                    </Badge>
                                </div>
                                <h2 className="text-lg font-bold text-slate-900 dark:text-white mt-2">
                                    {selectedSession.goal}
                                </h2>
                            </div>

                            {/* HITL Approval Gate Alert Box */}
                            {selectedSession.status === "awaiting_approval" && (
                                <div className="p-5 rounded-xl border border-amber-300 bg-amber-50 dark:bg-amber-950/30 dark:border-amber-800 space-y-3">
                                    <div className="flex items-center gap-2 text-amber-800 dark:text-amber-300 font-bold text-sm">
                                        <ShieldAlert className="h-5 w-5 text-amber-600" /> Human-in-the-Loop Authorization Required
                                    </div>
                                    <p className="text-xs text-amber-700 dark:text-amber-400 leading-relaxed">
                                        The agents have drafted a sensitive execution action ({selectedSession.pending_approval?.action_name || "Code Sandbox Execution"}). Please review the code before authorizing execution.
                                    </p>
                                    <div className="flex items-center gap-3 pt-2">
                                        <Button 
                                            onClick={() => handleDecision(true)} 
                                            className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs gap-1.5"
                                        >
                                            <CheckCircle2 className="h-4 w-4" /> Authorize & Execute
                                        </Button>
                                        <Button 
                                            onClick={() => handleDecision(false)} 
                                            variant="outline"
                                            className="border-red-300 text-red-700 hover:bg-red-50 dark:border-red-800 dark:text-red-300 text-xs gap-1.5"
                                        >
                                            <XCircle className="h-4 w-4" /> Reject Action
                                        </Button>
                                    </div>
                                </div>
                            )}

                            {/* Multi-Agent Blackboard Debate Entries */}
                            <div className="space-y-4">
                                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                                    <Layers className="h-4 w-4 text-slate-500" /> Multi-Turn Agent Dialogue
                                </h3>

                                {selectedSession.messages && selectedSession.messages.length > 0 ? (
                                    <div className="space-y-3">
                                        {selectedSession.messages.map((msg, idx) => {
                                            const msgTime = typeof msg.timestamp === "number" ? msg.timestamp * 1000 : Date.parse(msg.timestamp as any);
                                            return (
                                                <div key={idx} className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 space-y-2">
                                                    <div className="flex items-center justify-between">
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-xs font-bold text-slate-400 font-mono">Turn {idx + 1}</span>
                                                            {getRoleBadge(msg.sender_role)}
                                                            {msg.recipient_role && (
                                                                <span className="text-[10px] text-slate-400 font-mono">
                                                                    → {msg.recipient_role}
                                                                </span>
                                                            )}
                                                        </div>
                                                        <span className="text-[10px] text-slate-400 font-mono">
                                                            {isNaN(msgTime) ? "" : new Date(msgTime).toLocaleTimeString()}
                                                        </span>
                                                    </div>
                                                    <p className="text-xs leading-relaxed text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
                                                        {msg.content}
                                                    </p>
                                                </div>
                                            );
                                        })}
                                    </div>
                                ) : (
                                    <div className="p-6 text-center text-xs text-slate-400 border border-dashed rounded-lg">
                                        Agents are gathering research and deliberating on the blackboard...
                                    </div>
                                )}
                            </div>

                            {/* Final Synthesis */}
                            {selectedSession.final_synthesis && (
                                <div className="p-4 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-emerald-50/50 dark:bg-emerald-950/20 space-y-2">
                                    <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300 flex items-center gap-1.5">
                                        <CheckCircle2 className="h-4 w-4" /> Consensus Synthesis Solution
                                    </h3>
                                    <p className="text-xs leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-wrap">
                                        {selectedSession.final_synthesis}
                                    </p>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="py-20 text-center text-slate-400">
                            <Users className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                            <h3 className="text-base font-semibold text-slate-700 dark:text-slate-300">No Session Selected</h3>
                            <p className="text-xs text-slate-400 mt-1">Select a collaboration session from the sidebar or start a new debate.</p>
                        </div>
                    )}
                </div>
            </div>
        </section>
    );
}
