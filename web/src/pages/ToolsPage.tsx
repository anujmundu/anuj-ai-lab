import { useState, useEffect } from "react";
import { 
    Wrench, 
    Code, 
    Calculator, 
    FolderTree, 
    Eye, 
    Network, 
    Play, 
    Volume2, 
    Mic, 
    CheckCircle2, 
    Server,
    Sparkles
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { toolsService, type ToolDefinition } from "@/services/tools.service";
import { voiceService } from "@/services/voice.service";

interface BuiltinTool {
    name: string;
    label: string;
    description: string;
    icon: any;
    category: string;
    sampleInput: string;
}

const BUILTIN_TOOLS: BuiltinTool[] = [
    {
        name: "calculator",
        label: "AST Safe Calculator",
        description: "Evaluates mathematical expressions safely using Abstract Syntax Trees without eval().",
        icon: Calculator,
        category: "Math & Logic",
        sampleInput: "(128 * 4.5) / (2 ** 3) + math.sqrt(256)",
    },
    {
        name: "python_interpreter",
        label: "Python Subprocess Sandbox",
        description: "Executes Python code scripts locally in an isolated subprocess with memory and CPU ceilings.",
        icon: Code,
        category: "Code & Runtime",
        sampleInput: "import math\nprint({'squares': [x**2 for x in range(6)], 'pi_approx': round(math.pi, 4)})",
    },
    {
        name: "file_system",
        label: "Workspace FileSystem Tool",
        description: "Inspects directories, reads code files, and verifies paths within the workspace safely.",
        icon: FolderTree,
        category: "System & Files",
        sampleInput: "main.py",
    },
    {
        name: "knowledge_graph_query",
        label: "Knowledge Graph Explorer",
        description: "Queries extracted entity-relation subgraphs and performs multi-hop BFS neighborhood traversals.",
        icon: Network,
        category: "Knowledge Graph",
        sampleInput: "RAG",
    },
    {
        name: "vision_tool",
        label: "Vision Diagram OCR Tool",
        description: "Analyzes system architecture diagrams, charts, and scanned documents using local Vision LLMs.",
        icon: Eye,
        category: "Multi-Modal",
        sampleInput: "Describe the architecture diagram flow",
    },
];

export default function ToolsPage() {
    const [mcpTools, setMcpTools] = useState<ToolDefinition[]>([]);
    const [mcpServers, setMcpServers] = useState<any[]>([]);
    const [loadingMcp, setLoadingMcp] = useState(true);

    // Audio TTS / STT state
    const [ttsText, setTtsText] = useState("Welcome to Anuj AI Lab. All inference is running 100% locally.");
    const [selectedVoice, setSelectedVoice] = useState("af_sarah");
    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [ttsLoading, setTtsLoading] = useState(false);
    const [sttFile, setSttFile] = useState<File | null>(null);
    const [sttResult, setSttResult] = useState<string | null>(null);
    const [sttLoading, setSttLoading] = useState(false);

    // Tool Dry-Run Execution State
    const [activeTool, setActiveTool] = useState<string>("calculator");
    const [toolInput, setToolInput] = useState<string>("(128 * 4.5) / (2 ** 3) + math.sqrt(256)");
    const [executing, setExecuting] = useState(false);
    const [execResult, setExecResult] = useState<any>(null);

    useEffect(() => {
        async function fetchMcpData() {
            try {
                const [tools, servers] = await Promise.all([
                    toolsService.getMcpTools(),
                    toolsService.getMcpServers(),
                ]);
                setMcpTools(tools);
                setMcpServers(servers);
            } catch (err) {
                console.error("Failed to fetch MCP data", err);
            } finally {
                setLoadingMcp(false);
            }
        }
        fetchMcpData();
    }, []);

    async function handleSynthesizeSpeech() {
        if (!ttsText.trim()) return;
        setTtsLoading(true);
        try {
            const blob = await voiceService.synthesize(ttsText, selectedVoice);
            const url = URL.createObjectURL(blob);
            setAudioUrl(url);
        } catch (err: any) {
            console.error("TTS failed", err);
            alert("TTS Synthesis failed. Ensure Kokoro weights are in backend/models/kokoro/");
        } finally {
            setTtsLoading(false);
        }
    }

    async function handleTranscribeAudio() {
        if (!sttFile) return;
        setSttLoading(true);
        try {
            const res = await voiceService.transcribe(sttFile);
            setSttResult(res.text);
        } catch (err: any) {
            console.error("STT failed", err);
            alert("STT Transcription failed. Ensure faster-whisper is installed.");
        } finally {
            setSttLoading(false);
        }
    }

    async function handleRunTool(tool: BuiltinTool, overrideInput?: string) {
        const inputToRun = overrideInput ?? (tool.name === activeTool ? toolInput : tool.sampleInput);
        setActiveTool(tool.name);
        setToolInput(inputToRun);
        setExecuting(true);
        setExecResult(null);

        try {
            let params: Record<string, any> = {};
            if (tool.name === "calculator") {
                params = { expression: inputToRun };
            } else if (tool.name === "python_interpreter") {
                params = { code: inputToRun };
            } else if (tool.name === "file_system") {
                params = { action: "exists", path: inputToRun };
            } else if (tool.name === "knowledge_graph_query") {
                params = { query_type: "neighbors", entity_name: inputToRun, max_hops: 2 };
            } else {
                params = { query: inputToRun };
            }

            const res = await toolsService.executeTool(tool.name, params);
            setExecResult(res);
        } catch (err: any) {
            setExecResult({
                tool_name: tool.name,
                success: false,
                output: null,
                error: err.response?.data?.detail || err.message || "Execution error occurred.",
            });
        } finally {
            setExecuting(false);
        }
    }

    return (
        <section className="flex flex-1 flex-col gap-8 p-6 overflow-y-auto w-full">
            {/* Header */}
            <div>
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md">
                        <Wrench className="h-5 w-5" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                            Tools & Multi-Modal Studio
                        </h1>
                        <p className="text-slate-500 dark:text-slate-400 text-sm">
                            Inspect registered tools, test local Python sandboxes, execute Model Context Protocol (MCP) servers, and test offline voice STT/TTS.
                        </p>
                    </div>
                </div>
            </div>

            {/* Builtin Tools Catalog */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-indigo-500" /> Built-In System Tools
                    </h2>
                    <Badge variant="outline" className="border-indigo-200 text-indigo-700 dark:text-indigo-300">
                        {BUILTIN_TOOLS.length} Active Tools
                    </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {BUILTIN_TOOLS.map((tool) => {
                        const Icon = tool.icon;
                        const isSelected = activeTool === tool.name;
                        return (
                            <div 
                                key={tool.name}
                                className={`rounded-xl border p-5 transition-all cursor-pointer ${
                                    isSelected 
                                        ? "border-indigo-500 bg-indigo-50/40 dark:bg-indigo-950/20 shadow-md ring-1 ring-indigo-500" 
                                        : "border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-300"
                                }`}
                                onClick={() => handleRunTool(tool)}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-800 text-indigo-600 dark:text-indigo-400">
                                        <Icon className="h-5 w-5" />
                                    </div>
                                    <Badge variant="secondary" className="text-xs">
                                        {tool.category}
                                    </Badge>
                                </div>
                                <h3 className="mt-3 font-semibold text-slate-900 dark:text-white">
                                    {tool.label}
                                </h3>
                                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                                    {tool.description}
                                </p>
                                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                                    <span className="font-mono text-slate-400 truncate max-w-[180px]">{tool.sampleInput}</span>
                                    <span className="font-semibold text-indigo-600 dark:text-indigo-400 flex items-center gap-1">
                                        <Play className="h-3 w-3" /> Test
                                    </span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Dry Run Console & MCP Gateway */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Dry Run Execution Console */}
                <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm flex flex-col justify-between">
                    <div>
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                                <Play className="h-4 w-4 text-emerald-500" /> Interactive Dry-Run Console
                            </h3>
                            <Badge variant="outline" className="font-mono text-xs">{activeTool}</Badge>
                        </div>
                        <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                            Input Parameters / Expression:
                        </label>
                        <Input 
                            value={toolInput}
                            onChange={(e) => setToolInput(e.target.value)}
                            placeholder="Enter tool parameters..."
                            className="font-mono text-xs mb-3"
                        />
                        <Button 
                            onClick={() => {
                                const tool = BUILTIN_TOOLS.find(t => t.name === activeTool) || BUILTIN_TOOLS[0];
                                handleRunTool(tool);
                            }} 
                            disabled={executing}
                            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white"
                        >
                            {executing ? "Executing in Sandbox..." : "Execute Tool Dry-Run"}
                        </Button>
                    </div>

                    <div className="mt-4">
                        <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">
                            Execution Output:
                        </label>
                        <div className="rounded-lg bg-slate-950 p-4 font-mono text-xs text-emerald-400 min-h-[120px] max-h-[180px] overflow-auto">
                            {execResult ? (
                                <pre>{JSON.stringify(execResult, null, 2)}</pre>
                            ) : (
                                <span className="text-slate-600">// Click "Execute Tool Dry-Run" to view output...</span>
                            )}
                        </div>
                    </div>
                </div>

                {/* Model Context Protocol (MCP) Servers */}
                <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                            <Server className="h-4 w-4 text-purple-500" /> Model Context Protocol (MCP)
                        </h3>
                        <Badge variant="outline" className="border-purple-200 text-purple-700 dark:text-purple-300">
                            {mcpTools.length} Tools Connected
                        </Badge>
                    </div>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
                        Standard MCP client connecting your local agents to external tool servers over standard I/O streams.
                    </p>

                    {loadingMcp ? (
                        <div className="py-8 text-center text-xs text-slate-400">Loading MCP Servers...</div>
                    ) : mcpServers.length === 0 ? (
                        <div className="rounded-lg border border-dashed border-slate-200 dark:border-slate-800 p-6 text-center">
                            <CheckCircle2 className="h-8 w-8 text-emerald-500 mx-auto mb-2" />
                            <h4 className="font-semibold text-sm text-slate-900 dark:text-white">MCP Gateway Ready</h4>
                            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                                Standard MCP client manager is active on <code className="font-mono text-indigo-600">/mcp</code> with dynamic ToolAdapter support.
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {mcpServers.map((server, idx) => (
                                <div key={idx} className="flex items-center justify-between p-3 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                                    <span className="font-semibold text-xs text-slate-900 dark:text-white">{server.name}</span>
                                    <Badge variant="default" className="text-[10px] bg-emerald-600">Connected</Badge>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Offline Multi-Modal Audio Studio (STT & TTS) */}
            <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 shadow-sm space-y-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                            <Volume2 className="h-5 w-5 text-indigo-500" /> Offline Multi-Modal Voice Studio
                        </h3>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                            100% Offline Speech-to-Text (faster-whisper) and 24kHz Emotive Text-to-Speech (Kokoro-82M ONNX).
                        </p>
                    </div>
                    <Badge variant="outline" className="border-emerald-200 text-emerald-700 dark:text-emerald-300">
                        100% GPU / CPU Offline
                    </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* TTS Section */}
                    <div className="space-y-3 p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50">
                        <div className="flex items-center justify-between">
                            <h4 className="font-semibold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                                <Volume2 className="h-4 w-4 text-indigo-500" /> Kokoro-82M Voice Synthesis (TTS)
                            </h4>
                            <select
                                value={selectedVoice}
                                onChange={(e) => setSelectedVoice(e.target.value)}
                                className="text-xs font-mono font-medium bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg px-2 py-1 text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-indigo-500 cursor-pointer"
                            >
                                <option value="af_sarah">👩 Sarah (US Female)</option>
                                <option value="af_bella">👩 Bella (US Female)</option>
                                <option value="af_nicole">👩 Nicole (US Female)</option>
                                <option value="af_sky">👩 Sky (US Female)</option>
                                <option value="am_adam">👨 Adam (US Male)</option>
                                <option value="am_michael">👨 Michael (US Male)</option>
                                <option value="bf_emma">👩 Emma (UK Female)</option>
                                <option value="bf_isabella">👩 Isabella (UK Female)</option>
                                <option value="bm_george">👨 George (UK Male)</option>
                                <option value="bm_lewis">👨 Lewis (UK Male)</option>
                            </select>
                        </div>
                        <Input 
                            value={ttsText}
                            onChange={(e) => setTtsText(e.target.value)}
                            placeholder="Enter text to synthesize into speech..."
                            className="text-xs"
                        />
                        <Button 
                            onClick={handleSynthesizeSpeech} 
                            disabled={ttsLoading}
                            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-xs"
                        >
                            {ttsLoading ? "Generating 24kHz Audio..." : "Synthesize Voice Audio"}
                        </Button>
                        {audioUrl && (
                            <div className="pt-2">
                                <audio controls src={audioUrl} className="w-full h-9" autoPlay />
                            </div>
                        )}
                    </div>

                    {/* STT Section */}
                    <div className="space-y-3 p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50">
                        <h4 className="font-semibold text-sm text-slate-900 dark:text-white flex items-center gap-2">
                            <Mic className="h-4 w-4 text-emerald-500" /> Faster-Whisper Transcription (STT)
                        </h4>
                        <input 
                            type="file" 
                            accept="audio/*" 
                            onChange={(e) => setSttFile(e.target.files?.[0] || null)}
                            className="block w-full text-xs text-slate-500 file:mr-2 file:py-1 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 dark:file:bg-indigo-950 dark:file:text-indigo-300 cursor-pointer"
                        />
                        <Button 
                            onClick={handleTranscribeAudio} 
                            disabled={!sttFile || sttLoading}
                            className="w-full bg-emerald-600 hover:bg-emerald-700 text-white text-xs"
                        >
                            {sttLoading ? "Transcribing Audio..." : "Transcribe Speech to Text"}
                        </Button>
                        {sttResult && (
                            <div className="rounded bg-white dark:bg-slate-900 border p-3 text-xs text-slate-700 dark:text-slate-300">
                                <span className="font-semibold block mb-1">Transcription Result:</span>
                                {sttResult}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </section>
    );
}