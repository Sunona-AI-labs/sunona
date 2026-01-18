/**
 * Integrations Page - Sunona Style
 * All supported integrations and partners
 */

import Link from "next/link";
import { ArrowRight, ExternalLink } from "lucide-react";

const integrationCategories = [
    {
        title: "Telephony Providers",
        description: "Connect your existing phone infrastructure",
        integrations: [
            { name: "Twilio", icon: "📱", description: "Global cloud communications platform", status: "Available" },
            { name: "Plivo", icon: "☎️", description: "Cloud communications APIs", status: "Available" },
            { name: "Exotel", icon: "📞", description: "India's leading cloud telephony", status: "Available" },
            { name: "Vonage", icon: "🔊", description: "Unified communications APIs", status: "Available" },
            { name: "Telnyx", icon: "📲", description: "Real-time communications", status: "Coming Soon" },
        ],
    },
    {
        title: "LLM Providers",
        description: "Choose your preferred language model",
        integrations: [
            { name: "OpenAI", icon: "🤖", description: "GPT-4, GPT-3.5 models", status: "Available" },
            { name: "Anthropic", icon: "🧠", description: "Claude 3 models", status: "Available" },
            { name: "Azure OpenAI", icon: "☁️", description: "Enterprise OpenAI", status: "Available" },
            { name: "Groq", icon: "⚡", description: "Ultra-fast inference", status: "Available" },
            { name: "DeepSeek", icon: "🔍", description: "Cost-effective LLM", status: "Available" },
            { name: "OpenRouter", icon: "🔀", description: "Multi-model gateway", status: "Available" },
        ],
    },
    {
        title: "Speech-to-Text (ASR)",
        description: "Accurate transcription services",
        integrations: [
            { name: "Deepgram", icon: "👂", description: "Real-time speech recognition", status: "Available" },
            { name: "AssemblyAI", icon: "🎧", description: "AI-powered transcription", status: "Available" },
            { name: "Whisper", icon: "🗣️", description: "OpenAI speech recognition", status: "Available" },
            { name: "Google STT", icon: "🎤", description: "Google Cloud Speech", status: "Coming Soon" },
        ],
    },
    {
        title: "Text-to-Speech (TTS)",
        description: "Natural voice synthesis",
        integrations: [
            { name: "ElevenLabs", icon: "🎙️", description: "Ultra-realistic voices", status: "Available" },
            { name: "Cartesia", icon: "🔊", description: "Low-latency TTS", status: "Available" },
            { name: "PlayHT", icon: "▶️", description: "AI voice generation", status: "Available" },
            { name: "Rime", icon: "🎵", description: "Natural voice synthesis", status: "Available" },
            { name: "Azure TTS", icon: "☁️", description: "Microsoft neural voices", status: "Available" },
        ],
    },
    {
        title: "Automation & Workflow",
        description: "Connect to your existing tools",
        integrations: [
            { name: "Zapier", icon: "⚡", description: "5000+ app integrations", status: "Available" },
            { name: "Make.com", icon: "🔄", description: "Visual automation builder", status: "Available" },
            { name: "n8n", icon: "🔗", description: "Open-source workflow automation", status: "Available" },
            { name: "viaSocket", icon: "🔌", description: "No-code integrations", status: "Available" },
            { name: "Webhooks", icon: "🪝", description: "Custom HTTP callbacks", status: "Available" },
        ],
    },
    {
        title: "CRM & Databases",
        description: "Sync with your customer data",
        integrations: [
            { name: "Salesforce", icon: "☁️", description: "Enterprise CRM", status: "Coming Soon" },
            { name: "HubSpot", icon: "🧡", description: "Marketing & sales CRM", status: "Coming Soon" },
            { name: "Zoho", icon: "📊", description: "Business applications", status: "Coming Soon" },
            { name: "Airtable", icon: "📋", description: "Spreadsheet-database hybrid", status: "Available" },
            { name: "Google Sheets", icon: "📑", description: "Cloud spreadsheets", status: "Available" },
        ],
    },
];

export default function IntegrationsPage() {
    return (
        <div className="min-h-screen bg-[#0a0a0f] text-white">
            {/* Navigation */}
            <nav className="sticky top-0 z-50 bg-[#0a0a0f]/90 backdrop-blur-lg border-b border-white/5">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-sm">S</span>
                        </div>
                        <span className="text-xl font-bold">SUNONA</span>
                    </Link>

                    <div className="flex items-center gap-4">
                        <Link href="/login" className="text-gray-300 hover:text-white text-sm">Login</Link>
                        <Link
                            href="/signup"
                            className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-black font-medium rounded-lg text-sm"
                        >
                            Get Started
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero */}
            <section className="py-20 px-6 text-center">
                <span className="inline-block px-4 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full text-cyan-400 text-sm font-medium mb-4">
                    INTEGRATIONS
                </span>
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                    Seamless Integrations
                </h1>
                <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
                    Sunona works hand-in-hand with leading platforms to supercharge your communication stack.
                    Easily plug Sunona into your existing infrastructure and scale without friction.
                </p>

                {/* Integration Wheel */}
                <div className="relative w-72 h-72 mx-auto my-12">
                    <div className="absolute inset-0 border-2 border-white/10 rounded-full animate-spin-slow" style={{ animationDuration: '20s' }} />
                    <div className="absolute inset-8 border-2 border-white/5 rounded-full" />
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/25">
                        <span className="text-black font-bold text-2xl">S</span>
                    </div>

                    {/* Orbiting Icons */}
                    {["📱", "🤖", "👂", "🎙️", "⚡", "☁️"].map((icon, idx) => {
                        const angle = (idx * 60) - 90;
                        const x = Math.cos(angle * Math.PI / 180) * 120;
                        const y = Math.sin(angle * Math.PI / 180) * 120;
                        return (
                            <div
                                key={idx}
                                className="absolute w-12 h-12 bg-white/10 rounded-full flex items-center justify-center text-xl border border-white/20 shadow-lg"
                                style={{
                                    left: `calc(50% + ${x}px - 24px)`,
                                    top: `calc(50% + ${y}px - 24px)`,
                                }}
                            >
                                {icon}
                            </div>
                        );
                    })}
                </div>
            </section>

            {/* Integration Categories */}
            {integrationCategories.map((category) => (
                <section key={category.title} className="py-16 px-6 border-t border-white/5">
                    <div className="max-w-6xl mx-auto">
                        <div className="mb-8">
                            <h2 className="text-2xl font-bold mb-2">{category.title}</h2>
                            <p className="text-gray-400">{category.description}</p>
                        </div>

                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {category.integrations.map((int) => (
                                <div
                                    key={int.name}
                                    className="bg-white/5 border border-white/10 rounded-xl p-5 hover:border-cyan-500/30 transition-colors flex items-start gap-4"
                                >
                                    <span className="text-3xl">{int.icon}</span>
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-1">
                                            <h3 className="font-semibold">{int.name}</h3>
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${int.status === "Available"
                                                    ? "bg-green-500/20 text-green-400"
                                                    : "bg-yellow-500/20 text-yellow-400"
                                                }`}>
                                                {int.status}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-400">{int.description}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            ))}

            {/* BYOK Section */}
            <section className="py-20 px-6 bg-gradient-to-b from-transparent to-cyan-500/5">
                <div className="max-w-4xl mx-auto text-center">
                    <h2 className="text-3xl font-bold mb-4">Bring Your Own Keys (BYOK)</h2>
                    <p className="text-gray-400 mb-8">
                        Already have API keys from OpenAI, ElevenLabs, or other providers?
                        Connect them directly to Sunona and only pay for our platform fee.
                    </p>
                    <Link
                        href="/dashboard/providers"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg"
                    >
                        Connect Your Keys
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>
            </section>

            {/* CTA */}
            <section className="py-20 px-6 text-center">
                <h2 className="text-3xl font-bold mb-4">Need a Custom Integration?</h2>
                <p className="text-gray-400 mb-8">
                    Our team can help you build custom integrations for your specific needs.
                </p>
                <Link
                    href="/signup"
                    className="inline-flex items-center gap-2 px-6 py-3 border border-white/20 hover:bg-white/5 rounded-lg"
                >
                    Contact Sales
                    <ExternalLink className="w-4 h-4" />
                </Link>
            </section>

            {/* Footer */}
            <footer className="py-8 px-6 border-t border-white/10 text-center text-sm text-gray-500">
                <p>© 2025 Sunona Inc. All Rights Reserved.</p>
            </footer>
        </div>
    );
}
