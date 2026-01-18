/**
 * Providers Page - Light Theme
 * Connect and manage service providers
 */
"use client";

import * as React from "react";
import {
    Settings2,
    Search,
    CheckCircle,
    AlertCircle,
    ExternalLink,
    X,
} from "lucide-react";

const providerCategories = [
    { id: "all", label: "All Providers" },
    { id: "tts", label: "Text-to-Speech" },
    { id: "stt", label: "Speech-to-Text" },
    { id: "llm", label: "LLM" },
    { id: "telephony", label: "Telephony" },
];

const providers = [
    // TTS Providers
    { id: "elevenlabs", name: "ElevenLabs", category: "tts", logo: "🎙️", connected: true, description: "Premium AI voice synthesis" },
    { id: "azure-tts", name: "Azure TTS", category: "tts", logo: "☁️", connected: true, description: "Microsoft neural voices" },
    { id: "openai-tts", name: "OpenAI TTS", category: "tts", logo: "🤖", connected: false, description: "Natural sounding voices" },

    // STT Providers
    { id: "deepgram", name: "Deepgram", category: "stt", logo: "👂", connected: true, description: "Real-time transcription" },
    { id: "azure-stt", name: "Azure STT", category: "stt", logo: "☁️", connected: false, description: "Microsoft speech recognition" },

    // LLM Providers
    { id: "openai", name: "OpenAI", category: "llm", logo: "🤖", connected: true, description: "GPT-4, GPT-3.5 Turbo" },
    { id: "anthropic", name: "Anthropic", category: "llm", logo: "🧠", connected: true, description: "Claude 3 family" },
    { id: "groq", name: "Groq", category: "llm", logo: "⚡", connected: true, description: "Ultra-fast inference" },

    // Telephony Providers
    { id: "twilio", name: "Twilio", category: "telephony", logo: "📞", connected: true, description: "Global communications" },
    { id: "plivo", name: "Plivo", category: "telephony", logo: "☎️", connected: false, description: "Cloud communications" },
];

export default function ProvidersPage() {
    const [activeCategory, setActiveCategory] = React.useState("all");
    const [search, setSearch] = React.useState("");
    const [showConnectModal, setShowConnectModal] = React.useState(false);
    const [selectedProvider, setSelectedProvider] = React.useState<typeof providers[0] | null>(null);

    const filteredProviders = providers.filter((provider) => {
        if (activeCategory !== "all" && provider.category !== activeCategory) return false;
        if (search && !provider.name.toLowerCase().includes(search.toLowerCase())) return false;
        return true;
    });

    const handleConnect = (provider: typeof providers[0]) => {
        setSelectedProvider(provider);
        setShowConnectModal(true);
    };

    return (
        <div className="max-w-full">
            {/* Page Header */}
            <div className="mb-6">
                <h1 className="text-xl font-semibold text-gray-900">Providers</h1>
                <p className="text-sm text-gray-500 mt-1">
                    Connect and manage your TTS, STT, LLM, and Telephony providers
                </p>
            </div>

            {/* Category Tabs */}
            <div className="flex gap-2 mb-6">
                {providerCategories.map((cat) => (
                    <button
                        key={cat.id}
                        onClick={() => setActiveCategory(cat.id)}
                        className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${activeCategory === cat.id
                            ? "bg-blue-100 text-blue-700"
                            : "text-gray-600 hover:bg-gray-100"
                            }`}
                    >
                        {cat.label}
                    </button>
                ))}
            </div>

            {/* Search */}
            <div className="relative max-w-sm mb-6">
                <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none" style={{ paddingLeft: '14px' }}>
                    <Search className="w-4 h-4 text-gray-400" />
                </div>
                <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search providers..."
                    style={{ paddingLeft: '40px' }}
                    className="w-full pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all duration-200"
                />
            </div>




            {/* Providers Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredProviders.map((provider) => (
                    <div
                        key={provider.id}
                        className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                    >
                        <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl">
                                    {provider.logo}
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900">{provider.name}</h3>
                                    <p className="text-xs text-gray-500">{provider.description}</p>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between">
                            <span className={`flex items-center gap-1 text-xs font-medium ${provider.connected
                                ? "text-emerald-600"
                                : "text-gray-400"
                                }`}>
                                {provider.connected ? (
                                    <><CheckCircle className="w-3.5 h-3.5" /> Connected</>
                                ) : (
                                    <><AlertCircle className="w-3.5 h-3.5" /> Not connected</>
                                )}
                            </span>

                            {provider.connected ? (
                                <button className="flex items-center gap-1 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                                    <Settings2 className="w-4 h-4" />
                                    Settings
                                </button>
                            ) : (
                                <button
                                    onClick={() => handleConnect(provider)}
                                    className="flex items-center gap-1 px-3 py-1.5 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                                >
                                    Connect
                                    <ExternalLink className="w-3 h-3" />
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Connect Modal */}
            {showConnectModal && selectedProvider && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl max-w-md w-full">
                        <div className="flex items-center justify-between p-4 border-b border-gray-200">
                            <div className="flex items-center gap-3">
                                <span className="text-2xl">{selectedProvider.logo}</span>
                                <h3 className="text-lg font-semibold text-gray-900">Connect {selectedProvider.name}</h3>
                            </div>
                            <button onClick={() => setShowConnectModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
                                <input
                                    type="password"
                                    placeholder="Enter your API key..."
                                    className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <p className="text-xs text-gray-500">
                                Your API keys are encrypted and stored securely.{" "}
                                <a href="#" className="text-blue-600 hover:underline">Learn more</a>
                            </p>
                        </div>
                        <div className="flex justify-end gap-3 p-4 border-t border-gray-200">
                            <button onClick={() => setShowConnectModal(false)} className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                                Cancel
                            </button>
                            <button className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg">
                                Connect
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
