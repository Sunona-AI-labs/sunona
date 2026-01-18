/**
 * Documentation Portal - Sunona Style
 * API Reference, Voice AI Agents, Integrations, Tutorials
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import {
    Search,
    Book,
    Code,
    Bot,
    Plug,
    GraduationCap,
    ChevronRight,
    ExternalLink,
    Copy,
    CheckCircle,
    Home,
    FileText,
    Zap,
    Phone,
    Cpu,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { ComponentShowcase } from "@/components/docs/component-showcase";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Modal } from "@/components/ui/modal";
import { Mail, ArrowRight, Star, Heart, Info, AlertTriangle, AlertCircle } from "lucide-react";

// Tab definitions
const tabs = [
    { id: "documentation", label: "Documentation", icon: Book },
    { id: "components", label: "Components", icon: Cpu },
    { id: "api", label: "API Reference", icon: Code },
    { id: "agents", label: "Voice AI Agents", icon: Bot },
    { id: "integrations", label: "Integrations", icon: Plug },
    { id: "tutorials", label: "Examples & Tutorials", icon: GraduationCap },
];

// Sidebar sections for Documentation
const docSections = {
    "Getting Started": [
        { id: "home", label: "Home" },
        { id: "introduction", label: "Introduction" },
        { id: "platform-concepts", label: "Platform Concepts" },
        { id: "prompting-guide", label: "Prompting guide" },
        { id: "agents-library", label: "Agents Library" },
        { id: "import-agents", label: "Import agents" },
    ],
    "Pricing": [
        { id: "call-pricing", label: "Call Pricing" },
        { id: "concurrency", label: "Concurrency tiers" },
    ],
    "Enterprise": [
        { id: "enterprise-plan", label: "Enterprise plan" },
        { id: "sub-accounts", label: "Sub-Accounts" },
    ],
};

const componentSections = {
    "Foundation": [
        { id: "button", label: "Button" },
        { id: "badge", label: "Badge" },
        { id: "input", label: "Input" },
        { id: "card", label: "Card" },
    ],
    "Layout": [
        { id: "modal", label: "Modal" },
        { id: "skeleton", label: "Skeleton" },
    ],
    "Feedback": [
        { id: "error-boundary", label: "Error Boundary" },
    ],
};

// API sections
const apiSections = {
    "API Documentation": [
        { id: "introduction", label: "Introduction" },
        { id: "pagination", label: "Pagination" },
    ],
    "Current APIs": [
        {
            id: "agent", label: "Agent", items: [
                { id: "overview", label: "Overview" },
                { id: "get-agent", label: "Get agent" },
                { id: "create-agent", label: "Create agent" },
                { id: "update-agent", label: "Update agent" },
                { id: "patch-agent", label: "Patch update agent" },
                { id: "list-agents", label: "List agents" },
                { id: "get-execution", label: "Get agent execution" },
                { id: "all-executions", label: "Get all executions" },
            ]
        },
    ],
};

// Voice AI Agents
const voiceAgents = [
    { id: "recruitment", label: "Recruitment Agent", description: "AI-Powered Recruitment Screening & Interviewing" },
    { id: "customer-support", label: "Customer Support Agent", description: "24/7 intelligent customer assistance" },
    { id: "cart-abandonment", label: "Cart Abandonment Agent", description: "Recover abandoned carts" },
    { id: "lead-qualification", label: "Lead Qualification Agent", description: "Qualify leads automatically" },
    { id: "onboarding", label: "Onboarding Agent", description: "Guide new users" },
    { id: "front-desk", label: "Front Desk Agent", description: "Handle reception calls" },
    { id: "cod-confirmation", label: "COD Confirmation Agent", description: "Confirm cash on delivery orders" },
    { id: "announcements", label: "Announcements Agent", description: "Broadcast important updates" },
    { id: "reminders", label: "Reminders Agent", description: "Automated reminder calls" },
    { id: "surveys", label: "Surveys Agent", description: "Conduct voice surveys" },
    { id: "property-tech", label: "Property Tech Agent", description: "Real estate inquiries" },
    { id: "dentist", label: "Dentist Appointment Agent", description: "Schedule dental appointments" },
    { id: "salon", label: "Salon Booking Agent", description: "Book salon appointments" },
];

// Integrations
const integrations = {
    "Telephony Integrations": [
        { id: "twilio", label: "Twilio", description: "Connect your Twilio phone numbers" },
        { id: "plivo", label: "Plivo", description: "Connect your Plivo phone numbers" },
        { id: "exotel", label: "Exotel", description: "Connect your Exotel phone numbers" },
    ],
    "Model Integrations": [
        { id: "openai", label: "OpenAI", description: "Connect your OpenAI account" },
        { id: "deepseek", label: "Deepseek", description: "Connect Deepseek models" },
        { id: "groq", label: "Groq", description: "Connect Groq LLM" },
    ],
    "External Integrations": [
        { id: "make", label: "Make.com", description: "Build automations with Make" },
        { id: "zapier", label: "Zapier", description: "Connect with 5000+ apps" },
        { id: "n8n", label: "n8n", description: "Self-hosted automation" },
        { id: "viasocket", label: "viaSocket", description: "Real-time integrations" },
    ],
};

export default function DocsPage() {
    const [activeTab, setActiveTab] = React.useState("documentation");
    const [search, setSearch] = React.useState("");
    const [activeSection, setActiveSection] = React.useState("home");

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {/* Header */}
            <header className="border-b border-gray-800 sticky top-0 bg-gray-900 z-10">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-8">
                            <Link href="/dashboard" className="text-xl font-bold text-white flex items-center gap-2">
                                <span className="text-blue-400">Sunona</span>
                                <span className="text-gray-400">docs</span>
                            </Link>

                            {/* Tabs */}
                            <nav className="flex items-center gap-1">
                                {tabs.map((tab) => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`flex items-center gap-2 px-4 py-2 text-sm rounded-lg transition-colors ${activeTab === tab.id
                                            ? "bg-gray-800 text-white"
                                            : "text-gray-400 hover:text-white hover:bg-gray-800/50"
                                            }`}
                                    >
                                        <tab.icon className="w-4 h-4" />
                                        {tab.label}
                                    </button>
                                ))}
                            </nav>
                        </div>

                        <div className="flex items-center gap-4">
                            <Link href="#" className="text-sm text-gray-400 hover:text-white">Changelog</Link>
                            <Link href="#" className="text-sm text-gray-400 hover:text-white">Status</Link>
                            <Link href="#" className="text-sm text-gray-400 hover:text-white">Support</Link>
                            <Link href="/dashboard" className="text-sm text-blue-400 hover:text-blue-300">
                                Dashboard →
                            </Link>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto flex">
                {/* Sidebar */}
                <aside className="w-64 flex-shrink-0 border-r border-gray-800 min-h-[calc(100vh-65px)] p-4">
                    {/* Search */}
                    <div className="relative mb-6">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                        <input
                            type="text"
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            placeholder="Search..."
                            className="w-full pl-9 pr-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-500">Ctrl K</span>
                    </div>

                    {/* Sections */}
                    {activeTab === "documentation" && (
                        <DocsSidebar sections={docSections} active={activeSection} onSelect={setActiveSection} />
                    )}
                    {activeTab === "components" && (
                        <DocsSidebar sections={componentSections} active={activeSection} onSelect={setActiveSection} />
                    )}
                    {activeTab === "api" && (
                        <APISidebar sections={apiSections} active={activeSection} onSelect={setActiveSection} />
                    )}
                    {activeTab === "agents" && (
                        <AgentsSidebar agents={voiceAgents} active={activeSection} onSelect={setActiveSection} />
                    )}
                    {activeTab === "integrations" && (
                        <IntegrationsSidebar sections={integrations} active={activeSection} onSelect={setActiveSection} />
                    )}
                </aside>

                {/* Content Area */}
                <main className="flex-1 p-8">
                    {activeTab === "documentation" && <DocsContent section={activeSection} />}
                    {activeTab === "components" && <ComponentsContent section={activeSection} />}
                    {activeTab === "api" && <APIContent section={activeSection} />}
                    {activeTab === "agents" && <AgentsContent section={activeSection} agents={voiceAgents} />}
                    {activeTab === "integrations" && <IntegrationsContent section={activeSection} integrations={integrations} />}
                    {activeTab === "tutorials" && <TutorialsContent />}
                </main>

                {/* Right Sidebar - Table of Contents */}
                <aside className="w-56 flex-shrink-0 border-l border-gray-800 p-4">
                    <h4 className="text-xs font-medium text-gray-500 uppercase mb-4">On this page</h4>
                    <nav className="space-y-2 text-sm">
                        <a href="#" className="block text-blue-400">Overview</a>
                        <a href="#" className="block text-gray-400 hover:text-white">Key Features</a>
                        <a href="#" className="block text-gray-400 hover:text-white">Use Cases</a>
                        <a href="#" className="block text-gray-400 hover:text-white">How it Works</a>
                        <a href="#" className="block text-gray-400 hover:text-white">Getting Started</a>
                        <a href="#" className="block text-gray-400 hover:text-white">Next steps</a>
                    </nav>
                </aside>
            </div>
        </div>
    );
}

function DocsSidebar({ sections, active, onSelect }: { sections: any; active: string; onSelect: (id: string) => void }) {
    return (
        <nav className="space-y-6">
            {Object.entries(sections).map(([title, items]: [string, any]) => (
                <div key={title}>
                    <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">{title}</h3>
                    <div className="space-y-1">
                        {items.map((item: any) => (
                            <button
                                key={item.id}
                                onClick={() => onSelect(item.id)}
                                className={`w-full text-left px-3 py-1.5 text-sm rounded-lg transition-colors ${active === item.id ? "bg-blue-500/20 text-blue-400" : "text-gray-400 hover:text-white"
                                    }`}
                            >
                                {item.label}
                            </button>
                        ))}
                    </div>
                </div>
            ))}
        </nav>
    );
}

function APISidebar({ sections, active, onSelect }: { sections: any; active: string; onSelect: (id: string) => void }) {
    return (
        <nav className="space-y-6">
            {Object.entries(sections).map(([title, items]: [string, any]) => (
                <div key={title}>
                    <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">{title}</h3>
                    <div className="space-y-1">
                        {items.map((item: any) => (
                            <div key={item.id}>
                                {item.items ? (
                                    <>
                                        <div className="px-3 py-1.5 text-sm text-gray-300">{item.label}</div>
                                        <div className="ml-3 space-y-1">
                                            {item.items.map((subItem: any) => (
                                                <button
                                                    key={subItem.id}
                                                    onClick={() => onSelect(subItem.id)}
                                                    className={`w-full text-left px-3 py-1 text-xs rounded-lg transition-colors flex items-center gap-2 ${active === subItem.id ? "text-blue-400" : "text-gray-500 hover:text-gray-300"
                                                        }`}
                                                >
                                                    <span className="px-1.5 py-0.5 bg-gray-700 rounded text-[10px] font-mono">GET</span>
                                                    {subItem.label}
                                                </button>
                                            ))}
                                        </div>
                                    </>
                                ) : (
                                    <button
                                        onClick={() => onSelect(item.id)}
                                        className={`w-full text-left px-3 py-1.5 text-sm rounded-lg transition-colors ${active === item.id ? "bg-blue-500/20 text-blue-400" : "text-gray-400 hover:text-white"
                                            }`}
                                    >
                                        {item.label}
                                    </button>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </nav>
    );
}

function AgentsSidebar({ agents, active, onSelect }: { agents: any[]; active: string; onSelect: (id: string) => void }) {
    return (
        <nav>
            <h3 className="text-xs font-medium text-gray-500 uppercase mb-2">Voice AI Agents</h3>
            <div className="space-y-1">
                {agents.map((agent) => (
                    <button
                        key={agent.id}
                        onClick={() => onSelect(agent.id)}
                        className={`w-full text-left px-3 py-1.5 text-sm rounded-lg transition-colors ${active === agent.id ? "bg-blue-500/20 text-blue-400" : "text-gray-400 hover:text-white"
                            }`}
                    >
                        {agent.label}
                    </button>
                ))}
            </div>
        </nav>
    );
}

function IntegrationsSidebar({ sections, active, onSelect }: { sections: any; active: string; onSelect: (id: string) => void }) {
    return (
        <nav className="space-y-4">
            <button
                onClick={() => onSelect("sunona-integrations")}
                className={`w-full text-left px-3 py-1.5 text-sm rounded-lg transition-colors ${active === "sunona-integrations" ? "bg-blue-500/20 text-blue-400" : "text-gray-400 hover:text-white"
                    }`}
            >
                Sunona Integrations
            </button>
        </nav>
    );
}

function DocsContent({ section }: { section: string }) {
    if (section === "home") {
        return (
            <div className="max-w-4xl">
                <Badge variant="soft" className="mb-4">v2.4.0 Now Live</Badge>
                <h1 className="text-4xl font-extrabold text-white mb-6 tracking-tight">Sunona Voice AI Documentation</h1>
                <p className="text-zinc-400 text-lg mb-10 leading-relaxed">
                    Welcome to the official Sunona documentation. Learn how to create conversational voice agents that
                    <span className="text-blue-400 font-medium ml-1">qualify leads</span>,
                    <span className="text-blue-400 font-medium ml-1">boost sales</span>, and
                    <span className="text-blue-400 font-medium ml-1">automate support</span> with human-like latency and empathy.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
                    <Card variant="glow" hover className="p-6">
                        <Zap className="w-8 h-8 text-yellow-400 mb-4" />
                        <h3 className="text-lg font-semibold text-white mb-2">Introduction & Demo</h3>
                        <p className="text-zinc-500 text-sm leading-relaxed">Explore the core capabilities of Sunona and see our voice agents in action.</p>
                        <Button variant="link" className="mt-4 h-auto p-0">Learn more →</Button>
                    </Card>

                    <Card variant="bordered" hover className="p-6">
                        <Code className="w-8 h-8 text-blue-400 mb-4" />
                        <h3 className="text-lg font-semibold text-white mb-2">API Reference</h3>
                        <p className="text-zinc-500 text-sm leading-relaxed">Integrate Sunona into your existing workflows using our robust REST APIs.</p>
                        <Button variant="link" className="mt-4 h-auto p-0">View API docs →</Button>
                    </Card>
                </div>

                <div className="space-y-4">
                    <h2 className="text-xl font-bold text-white mb-4">Popular Guides</h2>
                    {[
                        { title: "Creating your first agent", duration: "5 min read", id: "introduction" },
                        { title: "Mastering Prompting Techniques", duration: "10 min read", id: "prompting-guide" },
                        { title: "Telephony Integration with Twilio", duration: "8 min read", id: "twilio" },
                    ].map((guide) => (
                        <div key={guide.id} className="flex items-center justify-between p-4 bg-zinc-900/30 border border-white/5 rounded-xl hover:border-white/10 transition-colors group cursor-pointer">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-zinc-800 rounded-lg group-hover:bg-blue-500/10 transition-colors">
                                    <Book className="w-5 h-5 text-zinc-400 group-hover:text-blue-400" />
                                </div>
                                <span className="font-medium text-zinc-300 group-hover:text-white transition-colors">{guide.title}</span>
                            </div>
                            <span className="text-xs text-zinc-600">{guide.duration}</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (section === "introduction") {
        return (
            <div className="max-w-3xl">
                <h1 className="text-3xl font-bold text-white mb-6">Introduction to Sunona</h1>
                <p className="text-zinc-400 mb-6 leading-relaxed">
                    Sunona is an Enterprise-grade Voice AI platform built for sub-100ms latency and high-fidelity conversations.
                    Our mission is to help businesses scale their voice interactions without sacrificing the quality of human connection.
                </p>
                <div className="space-y-8">
                    <section>
                        <h2 className="text-xl font-semibold text-white mb-3">What makes Sunona different?</h2>
                        <ul className="space-y-4">
                            <li className="flex gap-3">
                                <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />
                                <div>
                                    <span className="text-zinc-200 font-medium">Bilingual Support:</span>
                                    <p className="text-zinc-500 text-sm mt-1">Native-level fluency across multiple languages and regional dialects.</p>
                                </div>
                            </li>
                            <li className="flex gap-3">
                                <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />
                                <div>
                                    <span className="text-zinc-200 font-medium">Emotion Awareness:</span>
                                    <p className="text-zinc-500 text-sm mt-1">Real-time sentiment analysis to adjust tone and empathy during calls.</p>
                                </div>
                            </li>
                            <li className="flex gap-3">
                                <CheckCircle className="w-5 h-5 text-emerald-500 shrink-0" />
                                <div>
                                    <span className="text-zinc-200 font-medium">Low Latency Stack:</span>
                                    <p className="text-zinc-500 text-sm mt-1">Custom edge-processing to ensure no awkward pauses in conversation.</p>
                                </div>
                            </li>
                        </ul>
                    </section>
                </div>
            </div>
        );
    }

    if (section === "platform-concepts") {
        return (
            <div className="max-w-3xl">
                <h1 className="text-3xl font-bold text-white mb-6">Platform Concepts</h1>
                <p className="text-zinc-400 mb-8">Understanding the architecture and terminology used in the Sunona ecosystem.</p>

                <div className="grid gap-6">
                    {[
                        { title: "Agents", desc: "The core personality and brain of your voice AI. Defined by a system prompt and specific configuration." },
                        { title: "Executions", desc: "A single interaction or call instance. Contains logs, transcripts, and metadata." },
                        { title: "Providers", desc: "External services for STT (Speech-to-Text), LLM (Brain), and TTS (Text-to-Speech)." },
                        { title: "Campaigns", desc: "Orchestrated batches of calls targeted at specific customer segments." },
                    ].map((concept) => (
                        <Card key={concept.title} className="p-6 bg-zinc-900/20">
                            <h3 className="text-white font-semibold mb-2">{concept.title}</h3>
                            <p className="text-zinc-500 text-sm leading-relaxed">{concept.desc}</p>
                        </Card>
                    ))}
                </div>
            </div>
        );
    }

    if (section === "prompting-guide") {
        return (
            <div className="max-w-4xl">
                <h1 className="text-3xl font-bold text-white mb-4">Mastering Prompting Techniques</h1>
                <p className="text-zinc-400 mb-10 leading-relaxed text-lg">
                    System prompts are the most critical component of a Sunona agent. A well-structured prompt ensures
                    clatity, reduces hallucinations, and maintains the desired persona.
                </p>

                <div className="space-y-12">
                    <section>
                        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <span className="w-6 h-6 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-xs">1</span>
                            The "ACT" Framework
                        </h2>
                        <div className="grid md:grid-cols-3 gap-6">
                            <Card className="p-5 border-white/5 bg-zinc-900/10">
                                <h4 className="text-zinc-200 font-semibold mb-2">Role (A)</h4>
                                <p className="text-zinc-500 text-sm">Define who the agent is. "You are an empathetic customer support lead with 10 years experience."</p>
                            </Card>
                            <Card className="p-5 border-white/5 bg-zinc-900/10">
                                <h4 className="text-zinc-200 font-semibold mb-2">Context (C)</h4>
                                <p className="text-zinc-500 text-sm">Explain the situation. "The customer is calling about a delayed shipment for their order."</p>
                            </Card>
                            <Card className="p-5 border-white/5 bg-zinc-900/10">
                                <h4 className="text-zinc-200 font-semibold mb-2">Task (T)</h4>
                                <p className="text-zinc-500 text-sm">State the goal. "Your objective is to verify their details and provide a resolution or credit."</p>
                            </Card>
                        </div>
                    </section>

                    <section className="bg-zinc-900/30 border border-white/5 rounded-2xl p-8">
                        <h2 className="text-xl font-bold text-white mb-6">Expert Prompting Tips</h2>
                        <ul className="space-y-6">
                            <li className="flex gap-4">
                                <div className="p-2 bg-emerald-500/10 rounded-lg shrink-0 h-fit">
                                    <Zap className="w-5 h-5 text-emerald-400" />
                                </div>
                                <div>
                                    <h4 className="text-zinc-200 font-medium mb-1">Use Phonetic Spelling for Brand Names</h4>
                                    <p className="text-zinc-500 text-sm leading-relaxed">TTS models often struggle with unique names. Use "Soo-no-na" instead of "Sunona" in the prompt to ensure perfect pronunciation.</p>
                                </div>
                            </li>
                            <li className="flex gap-4">
                                <div className="p-2 bg-amber-500/10 rounded-lg shrink-0 h-fit">
                                    <Info className="w-5 h-5 text-amber-400" />
                                </div>
                                <div>
                                    <h4 className="text-zinc-200 font-medium mb-1">Implement Guardrails Early</h4>
                                    <p className="text-zinc-500 text-sm leading-relaxed">Explicitly state what the agent should NOT do. "Never discuss pricing without prior approval" or "Do not provide technical advice."</p>
                                </div>
                            </li>
                            <li className="flex gap-4">
                                <div className="p-2 bg-blue-500/10 rounded-lg shrink-0 h-fit">
                                    <GraduationCap className="w-5 h-5 text-blue-400" />
                                </div>
                                <div>
                                    <h4 className="text-zinc-200 font-medium mb-1">Few-Shot Examples</h4>
                                    <p className="text-zinc-500 text-sm leading-relaxed">Include 2-3 examples of ideal dialogues in the prompt. This helps the LLM mirror your desired conversational style and brevity.</p>
                                </div>
                            </li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-4">Example System Prompt</h2>
                        <div className="relative">
                            <pre className="p-6 bg-zinc-950 border border-white/10 rounded-xl overflow-x-auto font-mono text-sm text-zinc-400 leading-relaxed">
                                {`# Identity
You are Alex, a helpful representative from Sunona AI.

# Mission
Your goal is to qualify leads for our Enterprise Voice AI solution.

# Style Guidelines
- Keep responses short and conversational (1-2 sentences).
- Use a professional yet warm tone.
- Avoid robotic phrases like "How can I assist you today?".
- If they ask for pricing, mention we offer custom tiers for large organizations.`}
                            </pre>
                            <Button variant="ghost" size="sm" className="absolute top-4 right-4 text-zinc-600 hover:text-white">
                                <Copy className="w-4 h-4" />
                            </Button>
                        </div>
                    </section>
                </div>
            </div>
        );
    }

    if (section === "agents-library") {
        return (
            <div className="max-w-4xl">
                <h1 className="text-3xl font-bold text-white mb-6">Agents Library</h1>
                <p className="text-zinc-400 mb-8">Choose from our pre-built templates to get your voice assistant running in minutes.</p>

                <div className="grid md:grid-cols-2 gap-6">
                    {voiceAgents.slice(0, 4).map((agent) => (
                        <Card key={agent.id} className="p-6 border-white/5 bg-zinc-900/20 hover:border-blue-500/20 transition-all">
                            <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4">
                                <Bot className="w-6 h-6 text-blue-400" />
                            </div>
                            <h3 className="text-white font-semibold mb-2">{agent.label}</h3>
                            <p className="text-zinc-500 text-sm leading-relaxed">{agent.description}</p>
                            <Button variant="link" className="mt-4 p-0">Deploy template →</Button>
                        </Card>
                    ))}
                </div>
            </div>
        );
    }

    if (section === "import-agents") {
        return (
            <div className="max-w-3xl">
                <h1 className="text-3xl font-bold text-white mb-6">Importing Agents</h1>
                <p className="text-zinc-400 mb-8 leading-relaxed">
                    Already have agents configured in another platform? We support importing agent JSON definitions
                    directly into Sunona with minimal transformation required.
                </p>
                <div className="bg-zinc-800/40 border-l-4 border-blue-500 p-6 rounded-r-xl">
                    <h4 className="text-blue-400 font-semibold mb-2 flex items-center gap-2">
                        <Plug className="w-4 h-4" /> Migration Support
                    </h4>
                    <p className="text-zinc-400 text-sm">We currently support bulk imports from Vapi, Retell, and Bolna formatted JSONs.</p>
                </div>
            </div>
        );
    }

    if (section === "call-pricing") {
        return (
            <div className="max-w-4xl">
                <h1 className="text-3xl font-bold text-white mb-6 tracking-tight">Call Pricing</h1>
                <p className="text-zinc-400 mb-10 leading-relaxed text-lg">
                    Sunona offers a transparent, usage-based pricing model. You only pay for the minutes you use,
                    with no hidden platform fees for standard usage.
                </p>

                <div className="grid md:grid-cols-2 gap-8 mb-16">
                    <Card className="p-8 bg-zinc-900/20 border-white/5 hover:border-blue-500/20 transition-all">
                        <h3 className="text-zinc-200 font-semibold mb-3 flex items-center gap-3 text-xl">
                            <Phone className="w-6 h-6 text-blue-400" /> Inbound Calls
                        </h3>
                        <p className="text-zinc-500 text-sm mb-6 leading-relaxed">Flat rate for all incoming calls routed to your intelligent agents from any of your global numbers.</p>
                        <div className="text-3xl font-bold text-white">$0.15<span className="text-sm font-normal text-zinc-600 ml-2"> / minute</span></div>
                    </Card>
                    <Card className="p-8 bg-zinc-900/20 border-white/5 hover:border-yellow-500/20 transition-all">
                        <h3 className="text-zinc-200 font-semibold mb-3 flex items-center gap-3 text-xl">
                            <Zap className="w-6 h-6 text-yellow-400" /> Outbound Calls
                        </h3>
                        <p className="text-zinc-500 text-sm mb-6 leading-relaxed">Low-latency outbound dialing with industry-leading completion rates for automated outreach campaigns.</p>
                        <div className="text-3xl font-bold text-white">$0.20<span className="text-sm font-normal text-zinc-600 ml-2"> / minute</span></div>
                    </Card>
                </div>

                <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-white/5 rounded-3xl p-10 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-8 opacity-10">
                        <Zap className="w-24 h-24 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-white mb-4">Volume Discounts</h2>
                    <p className="text-zinc-400 text-sm mb-8 leading-relaxed max-w-xl">
                        For organizations exceeding 100,000 minutes per month, we provide custom volume-based pricing and dedicated infrastructure.
                        Contact our sales engineering team to discuss a tailored plan for your organization.
                    </p>
                    <Button variant="cyan" glow>Contact Sales Engineering</Button>
                </div>
            </div>
        );
    }

    if (section === "concurrency") {
        return (
            <div className="max-w-4xl">
                <h1 className="text-3xl font-bold text-white mb-6 tracking-tight">Concurrency Tiers</h1>
                <p className="text-zinc-400 mb-10 leading-relaxed text-lg">
                    Concurrency refers to the number of simultaneous active calls your organization can handle.
                    Sunona automatically scales capacity to meet your demand within your tier's limits.
                </p>

                <div className="space-y-4">
                    {[
                        { tier: "Developer", limit: "5 Concurrent Calls", price: "Free", color: "bg-zinc-500" },
                        { tier: "Startup", limit: "25 Concurrent Calls", price: "$49 / month", color: "bg-blue-500" },
                        { tier: "Growth", limit: "100 Concurrent Calls", price: "$199 / month", color: "bg-purple-500" },
                        { tier: "Enterprise", limit: "Unlimited (Custom)", price: "Contact Sales", color: "bg-emerald-500" },
                    ].map((t) => (
                        <div key={t.tier} className="flex items-center justify-between p-6 bg-zinc-900/30 border border-white/5 rounded-2xl hover:bg-zinc-900/50 transition-colors">
                            <div className="flex items-center gap-5">
                                <div className={cn("w-3 h-3 rounded-full shadow-[0_0_12px_currentColor]", t.color)} />
                                <div>
                                    <h4 className="text-white font-bold text-lg">{t.tier} Tier</h4>
                                    <Badge variant="mono" className="mt-1">{t.limit}</Badge>
                                </div>
                            </div>
                            <span className="text-zinc-300 font-bold text-xl">{t.price}</span>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    if (section === "enterprise-plan") {
        return (
            <div className="max-w-4xl">
                <h1 className="text-3xl font-bold text-white mb-6 tracking-tight">Enterprise Solution</h1>
                <p className="text-zinc-400 mb-12 leading-relaxed text-lg">
                    Our Enterprise plan is designed for high-scale, mission-critical voice automation.
                    Shift from shared infrastructure to dedicated compute and white-glove support.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <Card className="p-8 bg-zinc-950/40 border-emerald-500/20">
                        <div className="w-12 h-12 bg-emerald-500/10 rounded-xl flex items-center justify-center mb-6">
                            <Cpu className="w-6 h-6 text-emerald-400" />
                        </div>
                        <h4 className="text-white font-bold text-xl mb-3">Dedicated Infrastructure</h4>
                        <p className="text-zinc-500 text-sm leading-relaxed">Get isolated compute instances with zero noisy-neighbor effects, ensuring consistent sub-50ms processing latency.</p>
                    </Card>
                    <Card className="p-8 bg-zinc-950/40 border-blue-500/20">
                        <div className="w-12 h-12 bg-blue-500/10 rounded-xl flex items-center justify-center mb-6">
                            <Plug className="w-6 h-6 text-blue-400" />
                        </div>
                        <h4 className="text-white font-bold text-xl mb-3">SSO & SAML</h4>
                        <p className="text-zinc-500 text-sm leading-relaxed">Integrate your existing identity providers (Okta, Azure AD) for secure, centralized team management.</p>
                    </Card>
                    <Card className="p-8 bg-zinc-950/40 border-purple-500/20">
                        <div className="w-12 h-12 bg-purple-500/10 rounded-xl flex items-center justify-center mb-6">
                            <Bot className="w-6 h-6 text-purple-400" />
                        </div>
                        <h4 className="text-white font-bold text-xl mb-3">Custom Fine-Tuned Models</h4>
                        <p className="text-zinc-500 text-sm leading-relaxed">Train specialized LLMs on your company's proprietary knowledge base for unparalleled agent accuracy.</p>
                    </Card>
                    <Card className="p-8 bg-zinc-950/40 border-amber-500/20">
                        <div className="w-12 h-12 bg-amber-500/10 rounded-xl flex items-center justify-center mb-6">
                            <Zap className="w-6 h-6 text-amber-400" />
                        </div>
                        <h4 className="text-white font-bold text-xl mb-3">Prioritized Support</h4>
                        <p className="text-zinc-500 text-sm leading-relaxed">24/7 dedicated Slack channel with our core engineers and a 1-hour SLA for critical issues.</p>
                    </Card>
                </div>
            </div>
        );
    }

    if (section === "sub-accounts") {
        return (
            <div className="max-w-4xl">
                <h1 className="text-3xl font-bold text-white mb-6 tracking-tight">Sub-Accounts & Permissions</h1>
                <p className="text-zinc-400 mb-10 leading-relaxed text-lg">
                    Manage complex organizational structures by delegating control to different departments or clients
                    while maintaining a centralized parent view.
                </p>

                <div className="space-y-12">
                    <section>
                        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Home className="w-5 h-5 text-blue-400" /> Organizational Hierarchy
                        </h2>
                        <div className="p-8 bg-zinc-950 border border-white/5 rounded-3xl">
                            <div className="flex flex-col gap-8">
                                <div className="p-5 bg-zinc-900 border border-blue-500/40 rounded-2xl relative">
                                    <Badge variant="cyan" className="absolute -top-3 left-6">Parent Org (Master Admin)</Badge>
                                    <span className="text-zinc-200 font-bold">Sunona Enterprise Dashboard</span>
                                </div>
                                <div className="ml-12 flex flex-col gap-6 relative">
                                    <div className="absolute -left-8 top-0 bottom-6 w-px bg-zinc-800" />
                                    <div className="p-5 bg-zinc-900/50 border border-white/5 rounded-2xl relative group hover:border-white/20 transition-colors">
                                        <div className="absolute -left-8 top-1/2 w-8 h-px bg-zinc-800" />
                                        <span className="text-zinc-400 text-sm font-semibold group-hover:text-zinc-200 transition-colors">Customer Support Dept.</span>
                                        <div className="text-[10px] text-zinc-600 font-mono mt-1 italic">Sub-Account ID: sa_82k91...</div>
                                    </div>
                                    <div className="p-5 bg-zinc-900/50 border border-white/5 rounded-2xl relative group hover:border-white/20 transition-colors">
                                        <div className="absolute -left-8 top-1/2 w-8 h-px bg-zinc-800" />
                                        <span className="text-zinc-400 text-sm font-semibold group-hover:text-zinc-200 transition-colors">Sales & Outreach Team</span>
                                        <div className="text-[10px] text-zinc-600 font-mono mt-1 italic">Sub-Account ID: sa_12p05...</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>

                    <section>
                        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Plug className="w-5 h-5 text-purple-400" /> Role-Based Access Control (RBAC)
                        </h2>
                        <div className="grid md:grid-cols-2 gap-5">
                            {[
                                { role: "Owner", desc: "Full administrative control over billing, team seats, and global API keys." },
                                { role: "Account Manager", desc: "Can manage agents, campaigns, and phone numbers within their assigned sub-account." },
                                { role: "Developer", desc: "Access to logs, execution details, and integration settings. No billing access." },
                                { role: "Analyst", desc: "Read-only access to call transcripts, analytics reports, and execution metrics." },
                            ].map((r) => (
                                <Card key={r.role} className="p-6 bg-zinc-900/20 border-white/5">
                                    <h4 className="text-zinc-100 font-bold mb-2 flex items-center gap-2">
                                        <CheckCircle className="w-4 h-4 text-emerald-500" /> {r.role}
                                    </h4>
                                    <p className="text-zinc-500 text-xs leading-relaxed">{r.desc}</p>
                                </Card>
                            ))}
                        </div>
                    </section>
                </div>
            </div>
        );
    }

    // Default return for unimplemented sections
    return (
        <div className="max-w-4xl p-12 border border-dashed border-white/10 rounded-3xl flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 bg-zinc-900 rounded-2xl flex items-center justify-center mb-6 border border-white/5">
                <FileText className="w-8 h-8 text-zinc-600" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-3">Content Coming Soon</h1>
            <p className="text-zinc-500 max-w-sm">
                We are currently drafting the documentation for <span className="text-white font-medium">{section}</span>.
                Please check back in a few days.
            </p>
        </div>
    );
}

function APIContent({ section }: { section: string }) {
    const [copied, setCopied] = React.useState(false);

    const copyCode = () => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-3xl font-bold">Sunona API Documentation</h1>
                <Button variant="outline" size="sm" onClick={copyCode} className="text-gray-300 border-gray-600">
                    {copied ? <CheckCircle className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                    Copy page
                </Button>
            </div>

            <p className="text-gray-400 mb-8">
                Use and leverage Sunona Voice AI using APIs through HTTP requests from any language in your applications and workflows.
            </p>

            <h2 className="text-xl font-semibold mb-4">What is the Sunona API?</h2>
            <p className="text-gray-400 mb-6">
                The Sunona API enables you to programmatically create, configure, and manage Voice AI agents from your applications.
                Build voice AI capabilities into your products using simple HTTP requests from any programming language.
            </p>

            <p className="text-gray-400 mb-6">
                Sunona API features consistent, resource-oriented URLs, handles application/json request bodies,
                returns responses in JSON format, and utilizes standard HTTP response codes, authentication methods, and HTTP verbs.
            </p>

            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
                <p className="text-amber-400 text-sm flex items-center gap-2">
                    <span className="font-semibold">⚡</span>
                    You must have a valid voice account to generate and use APIs
                </p>
            </div>
        </div>
    );
}

function AgentsContent({ section, agents }: { section: string; agents: any[] }) {
    const agent = agents.find((a) => a.id === section) || agents[0];

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <p className="text-sm text-gray-500 mb-2">Voice AI Agents</p>
                    <h1 className="text-3xl font-bold">{agent.label}</h1>
                </div>
                <Button variant="outline" size="sm" className="text-gray-300 border-gray-600">
                    <Copy className="w-4 h-4 mr-2" />
                    Copy page
                </Button>
            </div>

            <p className="text-gray-400 mb-8 text-lg">{agent.description}</p>

            <h2 className="text-xl font-semibold mb-4">Overview</h2>
            <p className="text-gray-400 mb-6">
                Transform your operations with our {agent.label} - a sophisticated voice AI that revolutionizes how organizations handle this use case.
                Unlike traditional methods that rely on manual processes and scheduling bottlenecks, this advanced system conducts comprehensive interactions through natural conversations,
                dramatically accelerating your workflow while ensuring quality outcomes.
            </p>
        </div>
    );
}

function IntegrationsContent({ section, integrations }: { section: string; integrations: any }) {
    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">Telephony Integrations</h1>
            <p className="text-gray-400 mb-8">
                ElevenLabs, Deepgram, and Zapier to enable seamless voice automation and workflows.
            </p>

            <h2 className="text-xl font-semibold mb-6">Telephony Integrations</h2>
            <div className="grid grid-cols-3 gap-4 mb-8">
                {integrations["Telephony Integrations"].map((int: any) => (
                    <Card key={int.id} className="bg-gray-800 border-gray-700 hover:border-gray-600 transition-colors">
                        <CardContent className="p-4 text-center">
                            <div className="w-12 h-12 bg-gray-700 rounded-lg mx-auto mb-3 flex items-center justify-center">
                                <Phone className="w-6 h-6 text-gray-400" />
                            </div>
                            <h3 className="font-medium text-white mb-1">Connect your {int.label} account</h3>
                            <p className="text-xs text-gray-500">{int.description}</p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            <h2 className="text-xl font-semibold mb-6">Model Integrations</h2>
            <div className="grid grid-cols-3 gap-4">
                {integrations["Model Integrations"].map((int: any) => (
                    <Card key={int.id} className="bg-gray-800 border-gray-700 hover:border-gray-600 transition-colors">
                        <CardContent className="p-4 text-center">
                            <div className="w-12 h-12 bg-gray-700 rounded-lg mx-auto mb-3 flex items-center justify-center">
                                <Cpu className="w-6 h-6 text-gray-400" />
                            </div>
                            <h3 className="font-medium text-white mb-1">Connect your {int.label}</h3>
                            <p className="text-xs text-gray-500">{int.description}</p>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}

function TutorialsContent() {
    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">Using Sunona AI with No-code Tools</h1>
            <p className="text-gray-400 mb-8">
                Build your custom workflows and applications using Sunona Voice AI integrations with popular automations tools like Make.com, Zapier and viaSocket
            </p>

            <h2 className="text-xl font-semibold mb-4">What are Sunona no-code integrations?</h2>
            <p className="text-gray-400 mb-6">
                Sunona Voice AI seamlessly integrates with popular automation platforms like Make.com, Zapier, n8n, and viaSocket.
                These integrations allow you to build powerful workflows that trigger actions before, during, or after voice calls—without writing any code.
            </p>

            <h2 className="text-xl font-semibold mb-4">Why use no-code tools with Sunona?</h2>
            <ul className="list-disc list-inside text-gray-400 space-y-2">
                <li>No coding required - build automations visually</li>
                <li>Connect with 5000+ apps and services</li>
                <li>Trigger calls based on events in other apps</li>
                <li>Save call data to your CRM, spreadsheets, or databases</li>
                <li>Build complex multi-step workflows</li>
            </ul>
        </div>
    );
}

function ComponentsContent({ section }: { section: string }) {
    return (
        <div className="max-w-4xl">
            <h1 className="text-4xl font-extrabold text-white mb-4 tracking-tight">UI Components</h1>
            <p className="text-zinc-500 text-lg mb-12">
                A collection of premium, industrial-style UI components built with Tailwind CSS and Lucide Icons.
                Designed for high-performance SaaS applications with a focus on aesthetics and professional layout.
            </p>

            <div className="space-y-16">
                <section id="button">
                    <ComponentShowcase
                        title="Button"
                        description="Versatile button component with multiple variants and states."
                        code={`// Standard variants
<Button variant="primary">Primary Action</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>
<Button variant="ghost">Ghost</Button>

// Premium variants
<Button variant="cyan" glow>Premium Cyan</Button>
<Button variant="subtle">Subtle</Button>
<Button variant="link">Link Style</Button>

// Loading state
<Button isLoading>Processing...</Button>`}
                    >
                        <div className="flex flex-wrap gap-4">
                            <Button variant="primary">Primary Action</Button>
                            <Button variant="secondary">Secondary</Button>
                            <Button variant="outline">Outline</Button>
                            <Button variant="ghost">Ghost</Button>
                            <Button variant="cyan" glow>Premium Cyan</Button>
                            <Button variant="subtle">Subtle</Button>
                            <Button variant="danger">Danger</Button>
                            <Button variant="link">Link Style</Button>
                            <Button isLoading>Processing</Button>
                        </div>
                    </ComponentShowcase>
                </section>

                <section id="badge">
                    <ComponentShowcase
                        title="Badge"
                        description="Status indicators and labels with clean typography."
                        code={`<Badge variant="default">Standard</Badge>
<Badge variant="success" dot={true}>Active</Badge>
<Badge variant="error" dot={true}>Error</Badge>
<Badge variant="cyan">New</Badge>
<Badge variant="mono">BUILD:2024</Badge>
<Badge variant="soft">Early Access</Badge>`}
                    >
                        <div className="flex flex-wrap gap-4">
                            <Badge variant="default">Standard</Badge>
                            <Badge variant="success" dot={true}>Success</Badge>
                            <Badge variant="warning" dot={true}>Warning</Badge>
                            <Badge variant="error" dot={true}>Critical</Badge>
                            <Badge variant="info">Information</Badge>
                            <Badge variant="cyan">New Feature</Badge>
                            <Badge variant="mono">BUILD:2024</Badge>
                            <Badge variant="soft">Early Access</Badge>
                        </div>
                    </ComponentShowcase>
                </section>

                <section id="input">
                    <ComponentShowcase
                        title="Input"
                        description="Form input components with support for icons and validation states."
                        code={`<Input 
    label="Email Address" 
    placeholder="name@example.com" 
    leftIcon={<Mail className="w-4 h-4" />} 
/>

<Input 
    label="Search" 
    placeholder="Find something..." 
    rightIcon={<ArrowRight className="w-4 h-4" />} 
/>

<Input 
    label="Invalid Field" 
    error="This field is required" 
    defaultValue="Invalid value" 
/>`}
                    >
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-2xl">
                            <Input
                                label="Email Address"
                                placeholder="name@example.com"
                                leftIcon={<Mail className="w-4 h-4" />}
                            />
                            <Input
                                label="Search"
                                placeholder="Find something..."
                                rightIcon={<ArrowRight className="w-4 h-4" />}
                            />
                            <Input
                                label="Success State"
                                placeholder="Valid input"
                                defaultValue="sunona.ai"
                                hint="Your workspace URL is available"
                            />
                            <Input
                                label="Error State"
                                error="This field is required"
                                defaultValue=""
                                placeholder="Empty field"
                            />
                        </div>
                    </ComponentShowcase>
                </section>

                <section id="card">
                    <ComponentShowcase
                        title="Card"
                        description="Container for content with various visual styles."
                        code={`<Card className="p-6">Standard Container</Card>
<Card variant="glow" className="p-6">Premium Elevation</Card>
<Card variant="glass" className="p-6">Glassmorphism</Card>
<Card hover={true} className="p-6">Interactive State</Card>`}
                    >
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full">
                            <Card className="p-6">
                                <h4 className="text-lg font-semibold text-white mb-2 text-start">Standard Container</h4>
                                <p className="text-zinc-500 text-sm text-start leading-relaxed">Clean, minimal container with subtle borders for organizational structure and content spacing.</p>
                            </Card>
                            <Card variant="glow" className="p-6">
                                <h4 className="text-lg font-semibold text-white mb-2 text-start">Premium Elevation</h4>
                                <p className="text-zinc-500 text-sm text-start leading-relaxed">Enhanced with ambient glow for highlighting featured content, important metrics, or premium features.</p>
                            </Card>
                            <Card variant="glass" className="p-6">
                                <h4 className="text-lg font-semibold text-white mb-2 text-start">Glassmorphism</h4>
                                <p className="text-zinc-500 text-sm text-start leading-relaxed">Modern translucent backdrop with noise texture for tiered depth layering and visual sophistication.</p>
                            </Card>
                            <Card hover={true} className="p-6">
                                <h4 className="text-lg font-semibold text-white mb-2 text-start">Interactive State</h4>
                                <p className="text-zinc-500 text-sm text-start leading-relaxed">Smooth hover transitions with Y-axis translation and enhanced shadow depth for better affordance.</p>
                            </Card>
                        </div>
                    </ComponentShowcase>
                </section>
            </div>
        </div>
    );
}

