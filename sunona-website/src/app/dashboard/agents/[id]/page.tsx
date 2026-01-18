/**
 * Agent Edit Page - Sunona Dashboard (Light Theme)
 * 8 Configuration Tabs: Agent, LLM, Audio, Engine, Call, Tools, Analytics, Inbound
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
    ArrowLeft,
    Bot,
    Brain,
    AudioLines,
    Cog,
    Phone,
    Wrench,
    BarChart3,
    PhoneIncoming,
    Save,
    ExternalLink,
    Copy,
    Plus,
    MessageSquare,
    Sparkles,
    Share2,
} from "lucide-react";

// Tab definitions
const tabs = [
    { id: "agent", label: "Agent", icon: <Bot className="w-4 h-4" /> },
    { id: "llm", label: "LLM", icon: <Brain className="w-4 h-4" /> },
    { id: "audio", label: "Audio", icon: <AudioLines className="w-4 h-4" /> },
    { id: "engine", label: "Engine", icon: <Cog className="w-4 h-4" /> },
    { id: "call", label: "Call", icon: <Phone className="w-4 h-4" /> },
    { id: "tools", label: "Tools", icon: <Wrench className="w-4 h-4" /> },
    { id: "analytics", label: "Analytics", icon: <BarChart3 className="w-4 h-4" /> },
    { id: "inbound", label: "Inbound", icon: <PhoneIncoming className="w-4 h-4" /> },
];

// Mock agent data
const mockAgent = {
    id: "agent-1",
    name: "(v2) Customer Support - En + Hi - copy",
    welcomeMessage: "Hello, this is a demo call for Sunona's voice AI. Ready to get started?",
    systemPrompt: `SECTION 1: Demeanour & Identity

#Personality
[Agent Name – Anika] is a warm, empathetic, and grounded customer support agent who creates a safe and welcoming environment for customers to share their concerns. She is approachable, patient, and attentive, making customers feel valued even when their queries are routine or repetitive. She balances professionalism with a natural, conversational style—always sounding supportive and human, never scripted or robotic.`,
    costPerMin: 0.094,
};

export default function AgentEditPage() {
    const params = useParams();
    const [activeTab, setActiveTab] = React.useState("agent");
    const [agent, setAgent] = React.useState(mockAgent);
    const [isSaving, setIsSaving] = React.useState(false);

    const handleSave = async () => {
        setIsSaving(true);
        await new Promise((r) => setTimeout(r, 1000));
        setIsSaving(false);
    };

    return (
        <div className="min-h-screen bg-[#FAFAFA]">
            <div className="flex">
                {/* Main Content */}
                <div className="flex-1">
                    {/* Header */}
                    <div className="bg-white border-b border-gray-200 px-6 py-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <Link
                                    href="/dashboard/agents"
                                    className="p-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors"
                                >
                                    <ArrowLeft className="w-5 h-5" />
                                </Link>
                                <div>
                                    <div className="flex items-center gap-2">
                                        <h1 className="text-lg font-semibold text-gray-900">
                                            {agent.name}
                                        </h1>
                                        <button className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700">
                                            <Share2 className="w-3 h-3" />
                                            Agent ID
                                        </button>
                                        <button className="text-gray-400 hover:text-gray-600">
                                            <Copy className="w-3.5 h-3.5" />
                                        </button>
                                    </div>
                                    <div className="flex items-center gap-3 mt-1">
                                        <span className="text-xs text-gray-500">
                                            Cost per min ~ ${agent.costPerMin.toFixed(4)}
                                        </span>
                                        <div className="flex gap-0.5 h-2 w-32">
                                            <div className="flex-1 bg-blue-400 rounded-l" title="Transcriber" />
                                            <div className="flex-1 bg-emerald-400" title="LLM" />
                                            <div className="flex-1 bg-purple-400" title="Voice" />
                                            <div className="flex-1 bg-orange-400 rounded-r" title="Telephony" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Platform Badge */}
                        <div className="mt-3 flex items-center gap-2">
                            <span className="px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-700 rounded">
                                Platform
                            </span>
                        </div>
                    </div>

                    {/* Tabs */}
                    <div className="bg-white border-b border-gray-200 px-6">
                        <div className="flex gap-1">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`flex items-center gap-2 px-3 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === tab.id
                                        ? "border-blue-600 text-blue-600"
                                        : "border-transparent text-gray-500 hover:text-gray-700"
                                        }`}
                                >
                                    {tab.icon}
                                    {tab.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Tab Content */}
                    <div className="p-6">
                        <div className="max-w-3xl">
                            {activeTab === "agent" && (
                                <>
                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Agent Welcome Message</h3>
                                        <textarea
                                            value={agent.welcomeMessage}
                                            onChange={(e) => setAgent({ ...agent, welcomeMessage: e.target.value })}
                                            rows={2}
                                            className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                            placeholder="Enter welcome message..."
                                        />
                                        <p className="text-xs text-gray-500 mt-2">
                                            This will be the initial message from the agent. You can use variables here using {"{variable_name}"}
                                        </p>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <h3 className="text-gray-900 font-medium">Agent Prompt</h3>
                                            <button className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700">
                                                <Sparkles className="w-4 h-4" />
                                                AI Edit
                                            </button>
                                        </div>
                                        <textarea
                                            value={agent.systemPrompt}
                                            onChange={(e) => setAgent({ ...agent, systemPrompt: e.target.value })}
                                            rows={10}
                                            className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm"
                                            placeholder="Enter system prompt..."
                                        />
                                        <p className="text-xs text-gray-500 mt-2">
                                            You can define variables in the prompt using {"{variable_name}"}
                                        </p>
                                    </div>
                                </>
                            )}

                            {activeTab === "llm" && (
                                <>
                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Choose LLM model</h3>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Provider</label>
                                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                                    <option>Azure</option>
                                                    <option>OpenAI</option>
                                                    <option>Anthropic</option>
                                                    <option>Groq</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Model</label>
                                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                                    <option>gpt-4.1-mini cluster</option>
                                                    <option>gpt-4-turbo</option>
                                                    <option>gpt-3.5-turbo</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <div className="grid grid-cols-2 gap-6">
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">
                                                    Tokens generated on each LLM output
                                                </label>
                                                <input
                                                    type="number"
                                                    defaultValue={399}
                                                    className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                />
                                                <p className="text-xs text-gray-500 mt-2">
                                                    Increasing tokens enables longer responses but increases latency
                                                </p>
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Temperature</label>
                                                <input
                                                    type="number"
                                                    defaultValue={0.2}
                                                    step={0.1}
                                                    min={0}
                                                    max={2}
                                                    className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                />
                                                <p className="text-xs text-gray-500 mt-2">
                                                    Increasing temperature enables heightened creativity, but increases chance of deviation from prompt
                                                </p>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Add knowledge base</h3>
                                        <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                            <option>Select Knowledge base</option>
                                            <option>Company FAQ</option>
                                            <option>Product Documentation</option>
                                        </select>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <h3 className="text-gray-900 font-medium">Add FAQs & Guardrails</h3>
                                            <Link href="#" className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
                                                Learn more
                                                <ExternalLink className="w-3 h-3" />
                                            </Link>
                                        </div>
                                        <button className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 border border-dashed border-gray-300 rounded-lg px-4 py-3 w-full justify-center">
                                            <Plus className="w-4 h-4" />
                                            Add a new block for FAQs & Guardrails
                                        </button>
                                    </div>
                                </>
                            )}

                            {activeTab === "audio" && (
                                <>
                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Language</h3>
                                        <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                            <option>English</option>
                                            <option>Hindi</option>
                                            <option>Tamil</option>
                                            <option>Telugu</option>
                                        </select>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Select transcriber</h3>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Provider</label>
                                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                                    <option>Deepgram</option>
                                                    <option>Azure STT</option>
                                                    <option>Google STT</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Model</label>
                                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                                    <option>nova-2</option>
                                                    <option>nova-1</option>
                                                    <option>whisper-large</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Keywords</h3>
                                        <input
                                            type="text"
                                            placeholder="Enter keywords to boost..."
                                            className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                        <p className="text-xs text-gray-500 mt-2">
                                            Enter certain keywords/proper nouns you'd want to boost while understanding user speech
                                        </p>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Select voice</h3>
                                        <div className="grid grid-cols-2 gap-4 mb-4">
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Provider</label>
                                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                                    <option>ElevenLabs</option>
                                                    <option>Azure TTS</option>
                                                    <option>OpenAI TTS</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Voice</label>
                                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                                    <option>Maya - Young Australian</option>
                                                    <option>Sarah - American</option>
                                                    <option>George - British</option>
                                                </select>
                                            </div>
                                        </div>
                                        {/* Voice sliders */}
                                        <div className="grid grid-cols-3 gap-4 mt-4">
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Buffer Size</label>
                                                <input type="range" min="40" max="200" defaultValue="100" className="w-full" />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Speed</label>
                                                <input type="range" min="0.5" max="2" step="0.1" defaultValue="1" className="w-full" />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Similarity</label>
                                                <input type="range" min="0" max="100" defaultValue="75" className="w-full" />
                                            </div>
                                        </div>
                                    </div>
                                </>
                            )}

                            {activeTab === "engine" && (
                                <>
                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Transcription & interruptions</h3>
                                        <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
                                            <div>
                                                <label className="text-sm text-gray-900">Generate precise transcript</label>
                                                <p className="text-xs text-gray-500">Agent will try to generate more precise transcripts during interruptions</p>
                                            </div>
                                            <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                        </div>
                                        <div>
                                            <label className="block text-sm text-gray-700 mb-2">
                                                Number of words to wait for before interrupting
                                            </label>
                                            <input
                                                type="number"
                                                defaultValue={2}
                                                className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            />
                                            <p className="text-xs text-gray-500 mt-2">
                                                Agent will not consider interruptions until 3 words (or if recipient says "Stopwords" such as Stop, Wait, Hold On)
                                            </p>
                                        </div>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Voice Response Rate Configuration</h3>
                                        <div className="grid grid-cols-3 gap-4">
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Response Rate</label>
                                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                                    <option>Custom</option>
                                                    <option>Fast</option>
                                                    <option>Normal</option>
                                                    <option>Slow</option>
                                                </select>
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Endpointing (in ms)</label>
                                                <input
                                                    type="number"
                                                    defaultValue={250}
                                                    className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm text-gray-700 mb-2">Linear delay (in ms)</label>
                                                <input
                                                    type="number"
                                                    defaultValue={500}
                                                    className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </>
                            )}

                            {activeTab === "call" && (
                                <>
                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Telephony Provider</h3>
                                        <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                            <option>Plivo</option>
                                            <option>Twilio</option>
                                            <option>Exotel</option>
                                        </select>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Voicemail detection</h3>
                                        <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
                                            <div>
                                                <label className="text-sm text-gray-900">Automatically disconnect call on voicemail detection</label>
                                                <p className="text-xs text-gray-500">Time allotted to analyze if the call has been answered by a machine. Default value is 2500 ms.</p>
                                            </div>
                                            <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                        </div>
                                        <div>
                                            <label className="block text-sm text-gray-700 mb-2">Time (seconds)</label>
                                            <input
                                                type="number"
                                                defaultValue={2.5}
                                                step={0.1}
                                                className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            />
                                        </div>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Call hangup modes</h3>
                                        <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
                                            <div>
                                                <label className="text-sm text-gray-900">Hangup calls on user silence</label>
                                                <p className="text-xs text-gray-500">Call will hangup if the user is not speaking</p>
                                            </div>
                                            <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                        </div>
                                        <div>
                                            <label className="block text-sm text-gray-700 mb-2">Time (seconds)</label>
                                            <input
                                                type="number"
                                                defaultValue={15}
                                                className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                            />
                                        </div>
                                    </div>
                                </>
                            )}

                            {activeTab === "tools" && (
                                <div className="bg-white border border-gray-200 rounded-lg p-6">
                                    <div className="flex items-center justify-between mb-4">
                                        <div>
                                            <h3 className="text-gray-900 font-medium">Function Tools for LLM Models</h3>
                                            <p className="text-sm text-gray-500">
                                                Connect external tools or APIs that your language model can call during conversations.
                                            </p>
                                        </div>
                                        <Link href="#" className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
                                            See examples and learn more
                                            <ExternalLink className="w-3 h-3" />
                                        </Link>
                                    </div>

                                    <div className="flex items-center gap-3 mb-6">
                                        <select className="flex-1 px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                            <option>Select functions</option>
                                            <option>check_order_status</option>
                                            <option>schedule_appointment</option>
                                            <option>transfer_call</option>
                                        </select>
                                        <button className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                                            <Plus className="w-4 h-4" />
                                            Add function
                                        </button>
                                    </div>

                                    <div className="border border-dashed border-gray-300 rounded-lg p-8 text-center">
                                        <Wrench className="w-8 h-8 text-gray-400 mx-auto mb-3" />
                                        <p className="text-gray-500">No functions added yet</p>
                                        <p className="text-xs text-gray-400 mt-1">Add functions to extend your agent's capabilities</p>
                                    </div>
                                </div>
                            )}

                            {activeTab === "analytics" && (
                                <>
                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Post call tasks</h3>
                                        <p className="text-sm text-gray-500 mb-4">
                                            Choose tasks to get executed after the agent conversation is complete
                                        </p>

                                        <div className="space-y-3">
                                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                                <div>
                                                    <label className="text-sm text-gray-900">Summarization</label>
                                                    <p className="text-xs text-gray-500">Generate a summary of the conversation automatically</p>
                                                </div>
                                                <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                            </div>

                                            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                                <div className="flex-1">
                                                    <label className="text-sm text-gray-900">Extraction</label>
                                                    <p className="text-xs text-gray-500">Extract structured information from the conversation according to a custom prompt provided</p>
                                                </div>
                                                <div className="flex items-center gap-4">
                                                    <div className="text-xs text-gray-500">
                                                        <div>user_name : Yield the name of the user</div>
                                                        <div>payment_mode : If user is...</div>
                                                    </div>
                                                    <input type="checkbox" className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
                                        <h3 className="text-gray-900 font-medium mb-4">Custom Analytics</h3>
                                        <p className="text-sm text-gray-500 mb-4">
                                            Post call tasks to extract data from the call
                                        </p>
                                        <button className="flex items-center gap-2 px-4 py-2.5 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                                            <Plus className="w-4 h-4" />
                                            Extract custom analytics
                                        </button>
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                                        <div className="flex items-center justify-between mb-4">
                                            <h3 className="text-gray-900 font-medium">Push all execution data to</h3>
                                            <Link href="#" className="text-sm text-blue-600 hover:text-blue-700">
                                                See all
                                            </Link>
                                        </div>
                                        <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                            <option>Select webhook</option>
                                            <option>Call Completed Hook</option>
                                            <option>Zapier Integration</option>
                                        </select>
                                    </div>
                                </>
                            )}

                            {activeTab === "inbound" && (
                                <div className="bg-white border border-gray-200 rounded-lg p-6">
                                    <h3 className="text-gray-900 font-medium mb-4">Inbound Call Configuration</h3>
                                    <p className="text-sm text-gray-500 mb-6">
                                        Configure how this agent handles incoming calls
                                    </p>

                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm text-gray-700 mb-2">Assigned Phone Number</label>
                                            <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                                <option>Select phone number</option>
                                                <option>+1 (555) 123-4567</option>
                                                <option>+91 98765 43210</option>
                                            </select>
                                        </div>

                                        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                            <div>
                                                <label className="text-sm text-gray-900">Enable inbound calls</label>
                                                <p className="text-xs text-gray-500">Allow this agent to receive incoming calls</p>
                                            </div>
                                            <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                        </div>

                                        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                            <div>
                                                <label className="text-sm text-gray-900">Record all calls</label>
                                                <p className="text-xs text-gray-500">Automatically record all inbound conversations</p>
                                            </div>
                                            <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Right Sidebar Actions */}
                <div className="w-72 border-l border-gray-200 bg-white p-4">
                    <div className="space-y-4">
                        {/* See all call logs */}
                        <Link
                            href={`/dashboard/calls?agent=${params.id}`}
                            className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-700"
                        >
                            See all call logs
                            <ExternalLink className="w-3.5 h-3.5" />
                        </Link>

                        {/* Save Button */}
                        <div>
                            <button
                                onClick={handleSave}
                                disabled={isSaving}
                                className="w-full py-2.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 rounded-lg transition-colors flex items-center justify-center gap-2"
                            >
                                {isSaving ? (
                                    <span>Saving...</span>
                                ) : (
                                    <>
                                        <Save className="w-4 h-4" />
                                        Save agent
                                    </>
                                )}
                            </button>
                            <p className="text-xs text-gray-500 text-center mt-2">
                                Last updated a day ago
                            </p>
                        </div>

                        {/* Chat with agent */}
                        <div>
                            <button className="w-full py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
                                <MessageSquare className="w-4 h-4" />
                                Chat with agent
                            </button>
                            <p className="text-xs text-gray-500 text-center mt-2">
                                Chat is the fastest way to test and refine the agent.
                            </p>
                        </div>

                        {/* Test via web call */}
                        <div>
                            <button className="w-full py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
                                <Phone className="w-4 h-4" />
                                Test via web call
                            </button>
                            <p className="text-xs text-gray-500 text-center mt-2">
                                Test your agent with voice calls.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
