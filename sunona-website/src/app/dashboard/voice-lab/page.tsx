/**
 * Voice Lab Page - Light Theme
 * Explore and manage voice options
 */
"use client";

import * as React from "react";
import {
    Mic2,
    Search,
    Play,
    Pause,
    Upload,
    Copy,
    Heart,
    Volume2,
    X,
} from "lucide-react";

const voiceCategories = [
    { id: "all", label: "All Voices" },
    { id: "popular", label: "Popular" },
    { id: "indian", label: "Indian Languages" },
    { id: "cloned", label: "My Clones" },
    { id: "imported", label: "Imported" },
];

const voices = [
    { id: "v1", name: "Sarah", provider: "ElevenLabs", language: "English (US)", gender: "Female", style: "Professional", popular: true },
    { id: "v2", name: "James", provider: "ElevenLabs", language: "English (UK)", gender: "Male", style: "Calm", popular: true },
    { id: "v3", name: "Priya", provider: "Azure", language: "Hindi", gender: "Female", style: "Friendly", popular: false },
    { id: "v4", name: "Raj", provider: "Azure", language: "Hindi", gender: "Male", style: "Professional", popular: false },
    { id: "v5", name: "Maya", provider: "ElevenLabs", language: "English (AU)", gender: "Female", style: "Young", popular: true },
    { id: "v6", name: "My Voice Clone", provider: "ElevenLabs", language: "English", gender: "Custom", style: "Custom", cloned: true },
];

export default function VoiceLabPage() {
    const [activeCategory, setActiveCategory] = React.useState("all");
    const [search, setSearch] = React.useState("");
    const [playingId, setPlayingId] = React.useState<string | null>(null);
    const [showCloneModal, setShowCloneModal] = React.useState(false);

    const filteredVoices = voices.filter((voice) => {
        if (activeCategory === "popular") return voice.popular;
        if (activeCategory === "cloned") return voice.cloned;
        return true;
    });

    return (
        <div className="max-w-full">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">Voice Lab</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Explore and manage voices for your AI agents
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                        <Upload className="w-4 h-4" />
                        Import Voice
                    </button>
                    <button
                        onClick={() => setShowCloneModal(true)}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <Mic2 className="w-4 h-4" />
                        Clone Voice
                    </button>
                </div>
            </div>

            {/* Category Tabs */}
            <div className="flex gap-2 mb-6">
                {voiceCategories.map((cat) => (
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
                    placeholder="Search voices..."
                    style={{ paddingLeft: '40px' }}
                    className="w-full pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all duration-200"
                />
            </div>




            {/* Voices Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredVoices.map((voice) => (
                    <div key={voice.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                        <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-medium text-sm">
                                    {voice.name[0]}
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900">{voice.name}</h3>
                                    <p className="text-xs text-gray-500">{voice.provider}</p>
                                </div>
                            </div>
                            <button className="text-gray-400 hover:text-red-500 transition-colors">
                                <Heart className="w-4 h-4" />
                            </button>
                        </div>

                        <div className="flex flex-wrap gap-2 mb-3">
                            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">{voice.language}</span>
                            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">{voice.gender}</span>
                            <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">{voice.style}</span>
                        </div>

                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setPlayingId(playingId === voice.id ? null : voice.id)}
                                className="flex-1 flex items-center justify-center gap-2 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm"
                            >
                                {playingId === voice.id ? (
                                    <><Pause className="w-4 h-4" /> Pause</>
                                ) : (
                                    <><Play className="w-4 h-4" /> Preview</>
                                )}
                            </button>
                            <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                                <Copy className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Clone Voice Modal */}
            {showCloneModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl max-w-md w-full">
                        <div className="flex items-center justify-between p-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Clone Your Voice</h3>
                            <button onClick={() => setShowCloneModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Voice Name</label>
                                <input
                                    type="text"
                                    placeholder="My Custom Voice"
                                    className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors cursor-pointer">
                                <Volume2 className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                                <p className="text-sm text-gray-600">Upload audio samples</p>
                                <p className="text-xs text-gray-400">MP3, WAV (min 30 seconds)</p>
                            </div>
                        </div>
                        <div className="flex justify-end gap-3 p-4 border-t border-gray-200">
                            <button onClick={() => setShowCloneModal(false)} className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                                Cancel
                            </button>
                            <button className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg">
                                Clone Voice
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
