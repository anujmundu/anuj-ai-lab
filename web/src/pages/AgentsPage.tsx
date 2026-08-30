import { useState, useEffect } from "react";
import { 
    Bot, 
    CheckCircle2, 
    Clock, 
    Sparkles, 
    ChevronRight,
    Terminal,
    RefreshCw
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { agentsService, type AgentTask } from "@/services/agents.service";

export default function AgentsPage() {
    const [goal, setGoal] = useState("Analyze the project architecture and generate a summary report.");
    const [maxSteps, setMaxSteps] = useState(8);
    const [tasks, setTasks] = useState<AgentTask[]>([]);
    const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const [loading, setLoading] = useState(true);

    const selectedTask = tasks.find((t) => t.task_id === selectedTaskId) || (tasks.length > 0 ? tasks[0] : null);

    async function loadTasks() {
        try {
            const data = await agentsService.listTasks();
            setTasks(data);
            setSelectedTaskId((currentId) => {
                if (currentId && data.some((t) => t.task_id === currentId)) {
                    return currentId;
                }
                return data.length > 0 ? data[0].task_id : null;
            });
        } catch (err) {
            console.error("Failed to load agent tasks", err);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        loadTasks();
        const interval = setInterval(loadTasks, 3000);
        return () => clearInterval(interval);
    }, []);

    async function handleCreateTask() {
        if (!goal.trim()) return;
        setSubmitting(true);
        try {
            const res = await agentsService.createTask(goal, maxSteps);
            setSelectedTaskId(res.task_id);
            await loadTasks();
        } catch (err: any) {
            alert(err.message || "Failed to create agent task");
        } finally {
            setSubmitting(false);
        }
    }

    return (
        <section className="flex flex-1 flex-col gap-6 p-6 overflow-y-auto w-full">
            {/* Header */}
            <div>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-600 text-white shadow-md">
                            <Bot className="h-5 w-5" />
                        </div>
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                                Autonomous ReAct Agent Studio
                            </h1>
                            <p className="text-slate-500 dark:text-slate-400 text-sm">
                                Submit high-level goals for autonomous DAG decomposition, tool calling, and self-correcting reflection.
                            </p>
                        </div>
                    </div>
                    <Button variant="outline" size="sm" onClick={loadTasks} className="flex items-center gap-1.5 text-xs">
                        <RefreshCw className="h-3.5 w-3.5" /> Refresh
                    </Button>
                </div>
            </div>

            {/* Task Submission Box */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm space-y-4">
                <div className="flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-purple-500" />
                    <span className="font-semibold text-sm text-slate-900 dark:text-white">New Autonomous Agent Task</span>
                </div>
                <div className="flex flex-col sm:flex-row gap-3">
                    <Input 
                        value={goal}
                        onChange={(e) => setGoal(e.target.value)}
                        placeholder="Define agent task goal (e.g. 'Calculate the compound revenue growth and inspect codebase structure')..."
                        className="text-xs flex-1"
                    />
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500 whitespace-nowrap">Max Steps:</span>
                        <Input 
                            type="number"
                            value={maxSteps}
                            onChange={(e) => setMaxSteps(Number(e.target.value))}
                            min={1}
                            max={20}
                            className="w-16 text-xs"
                        />
                        <Button 
                            onClick={handleCreateTask}
                            disabled={submitting || !goal.trim()}
                            className="bg-purple-600 hover:bg-purple-700 text-white text-xs whitespace-nowrap"
                        >
                            {submitting ? "Dispatching..." : "Launch Agent"}
                        </Button>
                    </div>
                </div>
            </div>

            {/* Main Agent Workspace */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Task History Sidebar */}
                <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 shadow-sm space-y-3">
                    <span className="text-xs font-bold uppercase tracking-wide text-slate-400 block mb-2">
                        Execution History ({tasks.length})
                    </span>

                    {loading ? (
                        <div className="py-8 text-center text-xs text-slate-400">Loading agent tasks...</div>
                    ) : tasks.length === 0 ? (
                        <div className="py-8 text-center text-xs text-slate-400">No agent tasks yet. Launch your first task above!</div>
                    ) : (
                        <div className="space-y-2 max-h-[600px] overflow-y-auto">
                            {tasks.map((t) => {
                                const isSelected = selectedTask?.task_id === t.task_id;
                                const timestamp = typeof t.created_at === "number" ? t.created_at * 1000 : Date.parse(t.created_at);
                                return (
                                    <div 
                                        key={t.task_id}
                                        onClick={() => setSelectedTaskId(t.task_id)}
                                        className={`p-3 rounded-lg border transition-all cursor-pointer ${
                                            isSelected 
                                                ? "border-purple-500 bg-purple-50/40 dark:bg-purple-950/20 shadow-sm ring-1 ring-purple-500" 
                                                : "border-slate-100 dark:border-slate-800 hover:border-slate-300"
                                        }`}
                                    >
                                        <div className="flex items-center justify-between gap-2 mb-1">
                                            <Badge 
                                                variant={
                                                    t.status === "completed" ? "default" :
                                                    t.status === "failed" ? "destructive" : "secondary"
                                                }
                                                className="text-[10px] uppercase font-bold"
                                            >
                                                {t.status}
                                            </Badge>
                                            <span className="text-[10px] text-slate-400 font-mono">
                                                {isNaN(timestamp) ? "" : new Date(timestamp).toLocaleTimeString()}
                                            </span>
                                        </div>
                                        <p className="text-xs font-semibold text-slate-800 dark:text-slate-200 line-clamp-2">
                                            {t.goal}
                                        </p>
                                        <div className="mt-2 text-[10px] text-slate-400 flex items-center justify-between">
                                            <span>{t.steps?.length || 0} Steps executed</span>
                                            <ChevronRight className="h-3 w-3 text-slate-400" />
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Live Thought Trace & Step Inspector */}
                <div className="lg:col-span-2 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-6">
                    {selectedTask ? (
                        <>
                            <div className="border-b border-slate-100 dark:border-slate-800 pb-4">
                                <div className="flex items-center justify-between">
                                    <Badge variant="outline" className="font-mono text-xs text-purple-600 dark:text-purple-400 border-purple-200">
                                        Task: {selectedTask.task_id}
                                    </Badge>
                                    <Badge 
                                        variant={
                                            selectedTask.status === "completed" ? "default" :
                                            selectedTask.status === "failed" ? "destructive" : "secondary"
                                        }
                                        className="text-xs"
                                    >
                                        {selectedTask.status.toUpperCase()}
                                    </Badge>
                                </div>
                                <h2 className="text-lg font-bold text-slate-900 dark:text-white mt-2">
                                    {selectedTask.goal}
                                </h2>
                            </div>

                            {/* Plan Decomposition */}
                            {selectedTask.plan?.subtasks && selectedTask.plan.subtasks.length > 0 && (
                                <div className="p-4 rounded-xl border border-purple-100 dark:border-purple-950 bg-purple-50/50 dark:bg-purple-950/20">
                                    <h3 className="text-xs font-bold uppercase tracking-wider text-purple-700 dark:text-purple-300 flex items-center gap-1.5 mb-2">
                                        <Sparkles className="h-3.5 w-3.5" /> DAG Plan Decomposition
                                    </h3>
                                    <div className="space-y-1.5 font-mono text-xs text-slate-700 dark:text-slate-300">
                                        {selectedTask.plan.subtasks.map((st, idx) => (
                                            <div key={st.id || idx} className="flex items-center justify-between gap-2 p-2 rounded-lg bg-white/70 dark:bg-slate-900/70 border border-purple-100/50 dark:border-purple-900/30">
                                                <div className="flex items-center gap-2">
                                                    <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-purple-200 dark:bg-purple-800 text-[10px] font-bold text-purple-800 dark:text-purple-200">
                                                        {idx + 1}
                                                    </span>
                                                    <span>{st.description}</span>
                                                </div>
                                                {st.tool_name && (
                                                    <Badge variant="secondary" className="text-[10px] font-mono">
                                                        {st.tool_name}
                                                    </Badge>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* ReAct Execution Steps */}
                            <div className="space-y-4">
                                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                                    <Terminal className="h-4 w-4 text-slate-500" /> ReAct Reasoning & Execution Steps
                                </h3>

                                {selectedTask.steps && selectedTask.steps.length > 0 ? (
                                    <div className="space-y-3">
                                        {selectedTask.steps.map((s, idx) => (
                                            <div key={idx} className="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 space-y-2">
                                                <div className="flex items-center justify-between">
                                                    <span className="font-bold text-xs text-indigo-600 dark:text-indigo-400">
                                                        Step {s.step_number || idx + 1}: {s.action || "Reasoning"}
                                                    </span>
                                                    {s.success ? (
                                                        <span className="text-[10px] text-emerald-600 flex items-center gap-1 font-semibold">
                                                            <CheckCircle2 className="h-3 w-3" /> Success
                                                        </span>
                                                    ) : (
                                                        <span className="text-[10px] text-amber-600 flex items-center gap-1 font-semibold">
                                                            <Clock className="h-3 w-3" /> Executing
                                                        </span>
                                                    )}
                                                </div>

                                                {/* Thought */}
                                                {s.thought && (
                                                    <div className="text-xs text-slate-600 dark:text-slate-300">
                                                        <span className="font-semibold text-slate-800 dark:text-slate-100">💭 Thought: </span>
                                                        {s.thought}
                                                    </div>
                                                )}

                                                {/* Action & Tool Call */}
                                                {s.action && (
                                                    <div className="p-2.5 rounded bg-slate-900 text-emerald-400 font-mono text-[11px] overflow-auto">
                                                        <span className="text-slate-400 font-bold block mb-1">⚡ Action: {s.action}</span>
                                                        {s.action_input && (
                                                            <pre>{typeof s.action_input === "string" ? s.action_input : JSON.stringify(s.action_input, null, 2)}</pre>
                                                        )}
                                                    </div>
                                                )}

                                                {/* Observation */}
                                                {s.observation && (
                                                    <div className="p-2.5 rounded bg-slate-950 text-slate-300 font-mono text-[11px] overflow-auto max-h-32">
                                                        <span className="text-slate-500 font-bold block mb-1">👁️ Observation:</span>
                                                        <pre>{typeof s.observation === "string" ? s.observation : JSON.stringify(s.observation, null, 2)}</pre>
                                                    </div>
                                                )}

                                                {/* Reflection */}
                                                {s.reflection && (
                                                    <div className="text-xs text-amber-600 dark:text-amber-400 bg-amber-50/50 dark:bg-amber-950/20 p-2 rounded border border-amber-200/50">
                                                        <span className="font-semibold">🔄 Self-Correction Reflection: </span>
                                                        {s.reflection}
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="p-6 text-center text-xs text-slate-400 border border-dashed rounded-lg">
                                        Agent is currently reasoning and preparing step 1...
                                    </div>
                                )}
                            </div>

                            {/* Final Solution */}
                            {selectedTask.result && (
                                <div className="p-4 rounded-xl border border-emerald-200 dark:border-emerald-900 bg-emerald-50/50 dark:bg-emerald-950/20 space-y-2">
                                    <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-700 dark:text-emerald-300 flex items-center gap-1.5">
                                        <CheckCircle2 className="h-4 w-4" /> Synthesized Solution
                                    </h3>
                                    <p className="text-xs leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-wrap">
                                        {selectedTask.result}
                                    </p>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="py-20 text-center text-slate-400">
                            <Bot className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                            <h3 className="text-base font-semibold text-slate-700 dark:text-slate-300">No Task Selected</h3>
                            <p className="text-xs text-slate-400 mt-1">Select a task from the sidebar or launch a new task to view live execution traces.</p>
                        </div>
                    )}
                </div>
            </div>
        </section>
    );
}
