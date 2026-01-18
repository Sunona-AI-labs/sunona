/**
 * Agents Page - Enhanced UI with Working Tabs
 * Professional 21st.dev style with proper borders and styling
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    Plus,
    Bot,
    Phone,
    Copy,
    Check,
    Share2,
    ExternalLink,
    Import,
    Mic,
    Brain,
    Volume2,
    Cog,
    PhoneCall,
    Wrench,
    BarChart3,
    PhoneIncoming,
    Trash2,
    Play,
    Settings,
    Save,
    MessageSquare,
    X,
    Sparkles,
} from "lucide-react";

import { cn } from "@/lib/utils";

// Tab configuration
const tabs = [
    { id: "agent", label: "Agent", icon: Bot },
    { id: "llm", label: "LLM", icon: Brain },
    { id: "audio", label: "Audio", icon: Volume2 },
    { id: "engine", label: "Engine", icon: Cog },
    { id: "call", label: "Call", icon: PhoneCall },
    { id: "tools", label: "Tools", icon: Wrench },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "inbound", label: "Inbound", icon: PhoneIncoming },
];

// Mock data for agents
const mockAgents = [
    {
        agentId: "agent-1",
        name: "(v2) Customer Support - En + Hi - copy",
        description: "Handles customer inquiries and support tickets",
        costPerMinute: 0.094,
        transcriber: 0.02,
        llm: 0.03,
        voice: 0.025,
        telephony: 0.019,
        welcomeMessage: "Hello, this is a demo call for Customer Support AI. Ready to get started?",
        prompt: `SECTION 1: Demeanour & Identity

#Personality
[Agent Name – Anika] is a warm, empathetic, and grounded customer support agent who creates a safe and welcoming environment for customers to share their concerns...`,
    },
    {
        agentId: "agent-2",
        name: "Sales Outreach Agent",
        description: "Conducts outbound sales calls",
        costPerMinute: 0.112,
        transcriber: 0.025,
        llm: 0.04,
        voice: 0.03,
        telephony: 0.017,
        welcomeMessage: "Hi there! I'm calling from Sunona. Do you have a moment to chat?",
        prompt: `You are a professional sales agent focused on building rapport and understanding customer needs...`,
    },
];

export default function AgentsPage() {
    const router = useRouter();
    const [agents] = React.useState(mockAgents);
    const [selectedAgent, setSelectedAgent] = React.useState<string | null>(mockAgents[0]?.agentId || null);
    const [isLoading] = React.useState(false);

    return (
        <div className="flex gap-0 min-h-[calc(100vh-8rem)] -m-4 lg:-m-6">
            {/* Left Panel - Agent List */}
            <div className="w-72 shrink-0 border-r border-gray-200 bg-white">
                <div className="p-4">
                    {/* Page Header */}
                    <div className="mb-4">
                        <h1 className="text-lg font-semibold text-gray-900">Agent Setup</h1>
                        <p className="text-sm text-gray-500">Fine tune your agents</p>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2 mb-4">
                        <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors border border-gray-200">
                            <Import className="w-4 h-4" />
                            Import
                        </button>
                        <button
                            onClick={() => router.push("/dashboard/agents/new")}
                            className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors shadow-sm"
                        >
                            <Plus className="w-4 h-4" />
                            New Agent
                        </button>
                    </div>

                    {/* Your Agents Header */}
                    <div className="mb-3">
                        <h2 className="text-sm font-medium text-gray-900">Your Agents</h2>
                    </div>

                    {/* Agent List */}
                    {isLoading ? (
                        <div className="space-y-2">
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="h-16 bg-gray-100 rounded-lg animate-pulse" />
                            ))}
                        </div>
                    ) : agents.length > 0 ? (
                        <div className="space-y-2">
                            {agents.map((agent) => (
                                <button
                                    key={agent.agentId}
                                    onClick={() => setSelectedAgent(agent.agentId)}
                                    className={cn(
                                        "w-full flex items-center gap-3 p-3 rounded-lg transition-all text-left border",
                                        selectedAgent === agent.agentId
                                            ? "bg-blue-50 border-blue-200 shadow-sm"
                                            : "bg-white border-gray-200 hover:bg-gray-50 hover:border-gray-300"
                                    )}
                                >
                                    <div className={cn(
                                        "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
                                        selectedAgent === agent.agentId
                                            ? "bg-blue-500 text-white"
                                            : "bg-gray-100 text-gray-600"
                                    )}>
                                        <Bot size={16} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className={cn(
                                            "text-sm font-medium truncate",
                                            selectedAgent === agent.agentId ? "text-blue-900" : "text-gray-900"
                                        )}>
                                            {agent.name}
                                        </p>
                                        <p className="text-xs text-gray-500 truncate">
                                            ${agent.costPerMinute.toFixed(3)}/min
                                        </p>
                                    </div>
                                </button>
                            ))}
                        </div>
                    ) : (
                        <div className="p-6 text-center bg-gray-50 border border-gray-200 border-dashed rounded-lg">
                            <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                                <Bot className="w-5 h-5 text-gray-400" />
                            </div>
                            <p className="text-sm text-gray-500 mb-3">No agents yet.</p>
                            <button
                                onClick={() => router.push("/dashboard/agents/new")}
                                className="px-3 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
                            >
                                <Plus className="w-4 h-4 inline mr-1" />
                                Create Agent
                            </button>
                        </div>
                    )}
                </div>
            </div>

            {/* Center Panel - Agent Editor with Tabs */}
            <div className="flex-1 bg-gray-50 overflow-hidden flex flex-col">
                {selectedAgent ? (
                    <AgentEditorPanel
                        agent={agents.find(a => a.agentId === selectedAgent)!}
                    />
                ) : (
                    <div className="flex items-center justify-center h-full">
                        <div className="text-center">
                            <Bot className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                            <p className="text-gray-500">Select an agent to edit</p>
                        </div>
                    </div>
                )}
            </div>

            {/* Right Panel - Actions */}
            <div className="w-64 shrink-0 border-l border-gray-200 bg-white">
                {selectedAgent && (
                    <AgentActionPanel
                        agent={agents.find(a => a.agentId === selectedAgent)!}
                    />
                )}
            </div>
        </div>
    );
}

interface Agent {
    agentId: string;
    name: string;
    description: string;
    costPerMinute: number;
    transcriber?: number;
    llm?: number;
    voice?: number;
    telephony?: number;
    welcomeMessage?: string;
    prompt?: string;
}

function AgentEditorPanel({ agent }: { agent: Agent }) {
    const [activeTab, setActiveTab] = React.useState("agent");
    const [copied, setCopied] = React.useState(false);

    const handleCopyId = () => {
        navigator.clipboard.writeText(agent.agentId);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="h-full flex flex-col">
            {/* Agent Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <h2 className="text-lg font-semibold text-gray-900">{agent.name}</h2>
                        <button
                            onClick={handleCopyId}
                            className="flex items-center gap-1.5 px-2 py-1 text-xs text-gray-500 hover:text-gray-700 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                        >
                            {copied ? (
                                <>
                                    <Check className="w-3 h-3 text-green-500" />
                                    <span className="text-green-600">Copied!</span>
                                </>
                            ) : (
                                <>
                                    <Share2 className="w-3 h-3" />
                                    <span>Agent ID</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {/* Cost Breakdown */}
                <div className="mt-3 flex items-center gap-4">
                    <span className="text-sm text-gray-500">
                        Cost per min ~ <span className="font-medium text-gray-900">${agent.costPerMinute.toFixed(4)}</span>
                    </span>
                    <div className="flex gap-0.5 items-center">
                        <div className="w-16 h-2 bg-blue-400 rounded-l" title="Transcriber" />
                        <div className="w-20 h-2 bg-emerald-400" title="LLM" />
                        <div className="w-14 h-2 bg-purple-400" title="Voice" />
                        <div className="w-10 h-2 bg-orange-400 rounded-r" title="Telephony" />
                    </div>
                    <span className="px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-700 rounded">
                        Platform
                    </span>
                </div>
            </div>

            {/* Tabs - Proper Styling with Dividers */}
            <div className="bg-white border-b border-gray-200">
                <div className="flex px-4 items-center">
                    {tabs.map((tab, index) => (
                        <div key={tab.id} className="flex items-center">
                            <button
                                onClick={() => setActiveTab(tab.id)}
                                className={cn(
                                    "flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-all",
                                    activeTab === tab.id
                                        ? "text-blue-600 border-blue-600 bg-blue-50/50"
                                        : "text-gray-500 border-transparent hover:text-gray-700 hover:bg-gray-50"
                                )}
                            >
                                <tab.icon size={16} />
                                {tab.label}
                            </button>
                            {/* Divider between tabs */}
                            {index < tabs.length - 1 && (
                                <span className="text-gray-300 text-lg font-light px-1 select-none">|</span>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-y-auto p-6">
                <TabContent activeTab={activeTab} agent={agent} />
            </div>
        </div>
    );
}


function TabContent({ activeTab, agent }: { activeTab: string; agent: Agent }) {
    switch (activeTab) {
        case "agent":
            return <AgentTab agent={agent} />;
        case "llm":
            return <LLMTab />;
        case "audio":
            return <AudioTab />;
        case "engine":
            return <EngineTab />;
        case "call":
            return <CallTab />;
        case "tools":
            return <ToolsTab />;
        case "analytics":
            return <AnalyticsTab />;
        case "inbound":
            return <InboundTab />;
        default:
            return <AgentTab agent={agent} />;
    }
}

function AgentTab({ agent }: { agent: Agent }) {
    const [showAIEdit, setShowAIEdit] = React.useState(false);
    const [aiInstruction, setAiInstruction] = React.useState("");
    const [isEnhancing, setIsEnhancing] = React.useState(false);
    const [prompt, setPrompt] = React.useState(agent.prompt || "");

    const handleAIEnhance = () => {
        if (!aiInstruction.trim()) return;
        setIsEnhancing(true);
        // Simulate AI enhancement (in real app, this would call an API)
        setTimeout(() => {
            setPrompt(prev => `${prev}\n\n[AI Enhanced based on: "${aiInstruction}"]\n// Enhanced prompt content would appear here...`);
            setIsEnhancing(false);
            setShowAIEdit(false);
            setAiInstruction("");
        }, 1500);
    };

    return (
        <div className="max-w-2xl space-y-6">
            {/* AI Edit Modal - Industry Standard Design */}
            {showAIEdit && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 transition-opacity"
                        onClick={() => setShowAIEdit(false)}
                    />

                    {/* Modal Container - Centered */}
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                        <div
                            className="bg-white rounded-2xl shadow-2xl w-full max-w-lg pointer-events-auto border border-gray-200"
                            onClick={(e) => e.stopPropagation()}
                        >
                            {/* Modal Header */}
                            <div className="px-6 py-5 border-b border-gray-100">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center shadow-lg">
                                            <Sparkles className="w-5 h-5 text-white" />
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">AI Prompt Editor</h3>
                                            <p className="text-xs text-gray-500">Enhance your agent prompt with AI</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setShowAIEdit(false)}
                                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                    >
                                        <X size={20} className="text-gray-400 hover:text-gray-600" />
                                    </button>
                                </div>
                            </div>

                            {/* Modal Body */}
                            <div className="px-6 py-5">
                                <label className="block text-sm font-semibold text-gray-800 mb-3">
                                    How would you like to improve your prompt?
                                </label>
                                <textarea
                                    value={aiInstruction}
                                    onChange={(e) => setAiInstruction(e.target.value)}
                                    placeholder="Examples:&#10;• Make the agent more friendly and conversational&#10;• Add handling for frustrated customers&#10;• Include knowledge about product returns&#10;• Make responses shorter and more concise"
                                    className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white resize-none transition-all placeholder:text-gray-400"
                                    rows={5}
                                    autoFocus
                                />
                                <div className="mt-3 flex items-start gap-2 p-3 bg-blue-50 rounded-lg border border-blue-100">
                                    <Brain className="w-4 h-4 text-blue-600 mt-0.5 shrink-0" />
                                    <p className="text-xs text-blue-700">
                                        AI will analyze your current prompt and apply your instructions to create an enhanced version.
                                    </p>
                                </div>
                            </div>

                            {/* Modal Footer */}
                            <div className="px-6 py-4 border-t border-gray-100 bg-gray-50/50 rounded-b-2xl flex items-center justify-between">
                                <p className="text-xs text-gray-500">
                                    Press Escape to close
                                </p>
                                <div className="flex items-center gap-3">
                                    <button
                                        onClick={() => setShowAIEdit(false)}
                                        className="px-4 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleAIEnhance}
                                        disabled={!aiInstruction.trim() || isEnhancing}
                                        className="flex items-center gap-2 px-5 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed rounded-lg transition-all shadow-md hover:shadow-lg"
                                    >
                                        {isEnhancing ? (
                                            <>
                                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                                Enhancing...
                                            </>
                                        ) : (
                                            <>
                                                <Sparkles size={16} />
                                                Enhance Prompt
                                            </>
                                        )}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Agent Welcome Message */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                    Agent Welcome Message
                </label>
                <textarea
                    defaultValue={agent.welcomeMessage}
                    className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white resize-none transition-all"
                    rows={2}
                />
                <p className="mt-2 text-xs text-gray-500">
                    This will be the initial message from the agent. You can use variables here using {"{variable_name}"}
                </p>
            </div>

            {/* Agent Prompt */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-semibold text-gray-900">
                        Agent Prompt
                    </label>
                    <button
                        onClick={() => setShowAIEdit(true)}
                        className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-white bg-gradient-to-r from-purple-500 to-blue-600 hover:from-purple-600 hover:to-blue-700 rounded-lg transition-all shadow-sm"
                    >
                        <Sparkles size={12} />
                        AI Edit
                    </button>
                </div>
                <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white resize-none transition-all"
                    rows={10}
                />
                <p className="mt-2 text-xs text-gray-500">
                    You can define variables in the prompt using {"{variable_name}"}
                </p>
            </div>

            {/* Variables Section */}
            <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h4 className="text-sm font-semibold text-gray-900 mb-3">
                    Prompt Variables for Testing
                </h4>
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">variable_name</label>
                        <input
                            type="text"
                            placeholder="Enter value"
                            className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all"
                        />
                    </div>
                    <div>

                        <label className="block text-xs font-medium text-gray-600 mb-1.5">customer_name</label>
                        <input
                            type="text"
                            placeholder="Enter value"
                            className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 focus:bg-white transition-all"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

function LLMTab() {
    return (
        <div className="max-w-2xl space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">LLM Configuration</h3>

                <div className="space-y-4">
                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">Model Provider</label>
                        <select className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                            <option>OpenAI</option>
                            <option>Anthropic</option>
                            <option>Google Gemini</option>
                            <option>Groq</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">Model</label>
                        <select className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                            <option>gpt-4o</option>
                            <option>gpt-4o-mini</option>
                            <option>gpt-4-turbo</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">Temperature</label>
                        <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            defaultValue="0.7"
                            className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                            <span>Precise (0)</span>
                            <span>Creative (1)</span>
                        </div>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">Max Tokens</label>
                        <input
                            type="number"
                            defaultValue="150"
                            className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}

function AudioTab() {
    return (
        <div className="max-w-2xl space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Audio Configuration</h3>

                <div className="space-y-4">
                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">TTS Provider</label>
                        <select className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                            <option>ElevenLabs</option>
                            <option>OpenAI TTS</option>
                            <option>Azure TTS</option>
                            <option>Edge TTS</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">Voice</label>
                        <select className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                            <option>Rachel - Female (Warm)</option>
                            <option>Josh - Male (Professional)</option>
                            <option>Aria - Female (Energetic)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">STT Provider</label>
                        <select className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                            <option>Deepgram</option>
                            <option>OpenAI Whisper</option>
                            <option>AssemblyAI</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
    );
}

function EngineTab() {
    return (
        <div className="max-w-2xl space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Engine Settings</h3>

                <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <div>
                            <p className="text-sm font-medium text-gray-900">Interruption Handling</p>
                            <p className="text-xs text-gray-500">Allow user to interrupt the agent</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" defaultChecked className="sr-only peer" />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <div>
                            <p className="text-sm font-medium text-gray-900">End Call on Silence</p>
                            <p className="text-xs text-gray-500">Automatically end call after extended silence</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" defaultChecked className="sr-only peer" />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    );
}

function CallTab() {
    return (
        <div className="max-w-2xl space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Call Settings</h3>

                <div className="space-y-4">
                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">Max Call Duration (minutes)</label>
                        <input
                            type="number"
                            defaultValue="30"
                            className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
                        />
                    </div>

                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">Recording</label>
                        <select className="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all">
                            <option>Record all calls</option>
                            <option>Record on demand</option>
                            <option>Never record</option>
                        </select>
                    </div>
                </div>
            </div>
        </div>
    );
}

function ToolsTab() {
    return (
        <div className="max-w-2xl space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-semibold text-gray-900">Function Tools</h3>
                    <button className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors">
                        <Plus size={14} />
                        Add Tool
                    </button>
                </div>

                <div className="space-y-3">
                    <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                <Wrench size={14} className="text-blue-600" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-900">transfer_call</p>
                                <p className="text-xs text-gray-500">Transfer to human agent</p>
                            </div>
                        </div>
                        <button className="text-gray-400 hover:text-red-500">
                            <Trash2 size={14} />
                        </button>
                    </div>

                    <div className="p-3 bg-gray-50 rounded-lg border border-gray-200 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                <Wrench size={14} className="text-purple-600" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-gray-900">book_appointment</p>
                                <p className="text-xs text-gray-500">Schedule appointments</p>
                            </div>
                        </div>
                        <button className="text-gray-400 hover:text-red-500">
                            <Trash2 size={14} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

function AnalyticsTab() {
    return (
        <div className="max-w-2xl space-y-6">
            <div className="grid grid-cols-2 gap-4">
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-xs font-medium text-gray-500 mb-1">Total Calls</p>
                    <p className="text-2xl font-bold text-gray-900">1,234</p>
                    <p className="text-xs text-green-600 mt-1">+12% from last week</p>
                </div>
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-xs font-medium text-gray-500 mb-1">Avg Duration</p>
                    <p className="text-2xl font-bold text-gray-900">3:42</p>
                    <p className="text-xs text-gray-500 mt-1">minutes</p>
                </div>
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-xs font-medium text-gray-500 mb-1">Success Rate</p>
                    <p className="text-2xl font-bold text-gray-900">94.5%</p>
                    <p className="text-xs text-green-600 mt-1">+2% from last week</p>
                </div>
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                    <p className="text-xs font-medium text-gray-500 mb-1">Total Cost</p>
                    <p className="text-2xl font-bold text-gray-900">$234.50</p>
                    <p className="text-xs text-gray-500 mt-1">this month</p>
                </div>
            </div>
        </div>
    );
}

function InboundTab() {
    return (
        <div className="max-w-2xl space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
                <h3 className="text-sm font-semibold text-gray-900 mb-4">Inbound Number Configuration</h3>

                <div className="space-y-4">
                    <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1.5">Assigned Phone Number</label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value="+1 (555) 123-4567"
                                readOnly
                                className="flex-1 px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg text-sm text-gray-700"
                            />
                            <button className="px-3 py-2 text-sm text-blue-600 hover:bg-blue-50 border border-blue-200 rounded-lg transition-colors">
                                Change
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <div>
                            <p className="text-sm font-medium text-gray-900">Accept Inbound Calls</p>
                            <p className="text-xs text-gray-500">Allow this agent to receive calls</p>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" defaultChecked className="sr-only peer" />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    );
}

function AgentActionPanel({ agent }: { agent: Agent }) {
    const [isSaving, setIsSaving] = React.useState(false);
    const [saveSuccess, setSaveSuccess] = React.useState(false);
    const [showChatModal, setShowChatModal] = React.useState(false);
    const [showCallModal, setShowCallModal] = React.useState(false);
    const [showDeleteModal, setShowDeleteModal] = React.useState(false);
    const [isDeleting, setIsDeleting] = React.useState(false);
    const [chatMessage, setChatMessage] = React.useState("");
    const [chatMessages, setChatMessages] = React.useState<{ role: string; content: string }[]>([]);

    const handleSave = () => {
        setIsSaving(true);
        setTimeout(() => {
            setIsSaving(false);
            setSaveSuccess(true);
            setTimeout(() => setSaveSuccess(false), 2000);
        }, 1000);
    };

    const handleSendChat = () => {
        if (!chatMessage.trim()) return;
        setChatMessages(prev => [...prev, { role: "user", content: chatMessage }]);
        setChatMessage("");
        // Simulate agent response
        setTimeout(() => {
            setChatMessages(prev => [...prev, {
                role: "agent",
                content: "Hello! I'm your AI assistant. How can I help you today?"
            }]);
        }, 1000);
    };

    const handleDelete = () => {
        setIsDeleting(true);
        setTimeout(() => {
            setIsDeleting(false);
            setShowDeleteModal(false);
            // In real app, would delete agent and redirect
            alert("Agent deleted successfully!");
        }, 1500);
    };

    return (
        <div className="p-4 space-y-4">
            {/* Chat Modal */}
            {showChatModal && (
                <>
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" onClick={() => setShowChatModal(false)} />
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md pointer-events-auto border border-gray-200 flex flex-col h-[500px]">
                            <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                                        <MessageSquare className="w-4 h-4 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900">Chat with Agent</h3>
                                        <p className="text-xs text-gray-500">{agent.name}</p>
                                    </div>
                                </div>
                                <button onClick={() => setShowChatModal(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                                    <X size={18} className="text-gray-500" />
                                </button>
                            </div>
                            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
                                {chatMessages.length === 0 && (
                                    <p className="text-center text-gray-400 text-sm py-8">Start a conversation with your agent</p>
                                )}
                                {chatMessages.map((msg, i) => (
                                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm ${msg.role === 'user'
                                                ? 'bg-blue-600 text-white rounded-br-md'
                                                : 'bg-white border border-gray-200 text-gray-800 rounded-bl-md'
                                            }`}>
                                            {msg.content}
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div className="p-4 border-t border-gray-100 flex gap-2">
                                <input
                                    type="text"
                                    value={chatMessage}
                                    onChange={(e) => setChatMessage(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                                    placeholder="Type a message..."
                                    className="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                                />
                                <button
                                    onClick={handleSendChat}
                                    className="px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors"
                                >
                                    Send
                                </button>
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Web Call Modal */}
            {showCallModal && (
                <>
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" onClick={() => setShowCallModal(false)} />
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm pointer-events-auto border border-gray-200 text-center p-8">
                            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center mx-auto mb-5 animate-pulse">
                                <Phone className="w-8 h-8 text-white" />
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">Web Call Active</h3>
                            <p className="text-sm text-gray-500 mb-6">Speaking with {agent.name}</p>
                            <div className="flex items-center justify-center gap-3 mb-6">
                                <div className="flex gap-1">
                                    <div className="w-2 h-6 bg-green-500 rounded animate-pulse" />
                                    <div className="w-2 h-8 bg-green-500 rounded animate-pulse delay-75" />
                                    <div className="w-2 h-5 bg-green-500 rounded animate-pulse delay-150" />
                                    <div className="w-2 h-7 bg-green-500 rounded animate-pulse delay-100" />
                                    <div className="w-2 h-4 bg-green-500 rounded animate-pulse" />
                                </div>
                            </div>
                            <button
                                onClick={() => setShowCallModal(false)}
                                className="px-8 py-3 bg-red-500 hover:bg-red-600 text-white font-medium rounded-xl transition-colors shadow-lg"
                            >
                                End Call
                            </button>
                        </div>
                    </div>
                </>
            )}

            {/* Delete Confirmation Modal */}
            {showDeleteModal && (
                <>
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" onClick={() => setShowDeleteModal(false)} />
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
                        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm pointer-events-auto border border-gray-200 overflow-hidden">
                            <div className="p-6 text-center">
                                <div className="w-14 h-14 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
                                    <Trash2 className="w-6 h-6 text-red-600" />
                                </div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-2">Delete Agent?</h3>
                                <p className="text-sm text-gray-500 mb-4">
                                    Are you sure you want to delete "{agent.name}"? This action cannot be undone.
                                </p>
                            </div>
                            <div className="px-6 py-4 bg-gray-50 flex items-center justify-end gap-3 border-t border-gray-100">
                                <button
                                    onClick={() => setShowDeleteModal(false)}
                                    className="px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleDelete}
                                    disabled={isDeleting}
                                    className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 disabled:bg-red-400 rounded-lg transition-colors flex items-center gap-2"
                                >
                                    {isDeleting ? (
                                        <>
                                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            Deleting...
                                        </>
                                    ) : (
                                        <>
                                            <Trash2 size={14} />
                                            Delete Agent
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* See all call logs */}
            <Link
                href={`/dashboard/calls?agent=${agent.agentId}`}
                className="flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
                See all call logs
                <ExternalLink className="w-3.5 h-3.5" />
            </Link>

            {/* Action Buttons */}
            <div className="space-y-3">
                <button
                    onClick={handleSave}
                    disabled={isSaving}
                    className={`w-full py-2.5 text-sm font-medium text-white rounded-lg transition-all shadow-sm flex items-center justify-center gap-2 ${saveSuccess
                            ? 'bg-green-500 hover:bg-green-600'
                            : 'bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400'
                        }`}
                >
                    {isSaving ? (
                        <>
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            Saving...
                        </>
                    ) : saveSuccess ? (
                        <>
                            <Check size={16} />
                            Saved!
                        </>
                    ) : (
                        <>
                            <Save size={16} />
                            Save agent
                        </>
                    )}
                </button>
                <p className="text-xs text-gray-500 text-center">
                    Last updated a day ago
                </p>
            </div>

            <div className="pt-2 border-t border-gray-200 space-y-3">
                <button
                    onClick={() => setShowChatModal(true)}
                    className="flex items-center justify-center gap-2 w-full py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-colors"
                >
                    <MessageSquare size={16} />
                    Chat with agent
                </button>
                <p className="text-xs text-gray-500 text-center">
                    Chat is the fastest way to test and refine the agent.
                </p>
            </div>

            <div className="space-y-3">
                <button
                    onClick={() => setShowCallModal(true)}
                    className="flex items-center justify-center gap-2 w-full py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:border-gray-400 transition-colors"
                >
                    <Phone size={16} />
                    Test via web call
                </button>
                <p className="text-xs text-gray-500 text-center">
                    Test your agent with voice calls.
                </p>
            </div>

            {/* Danger Zone */}
            <div className="pt-4 mt-4 border-t border-gray-200">
                <button
                    onClick={() => setShowDeleteModal(true)}
                    className="flex items-center justify-center gap-2 w-full py-2.5 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 border border-red-200 hover:border-red-300 rounded-lg transition-colors"
                >
                    <Trash2 size={14} />
                    Delete agent
                </button>
            </div>
        </div>
    );
}
