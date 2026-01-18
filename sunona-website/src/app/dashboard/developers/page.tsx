/**
 * Developers Page - Light Theme
 * API keys and developer resources
 */
"use client";

import * as React from "react";
import Link from "next/link";
import {
    Code2,
    Key,
    Plus,
    Copy,
    Eye,
    EyeOff,
    Trash2,
    RefreshCw,
    ExternalLink,
    Book,
    Settings,
    X,
} from "lucide-react";

// Mock API keys
const mockApiKeys = [
    {
        id: "key-1",
        name: "Production Key",
        prefix: "sk_live_",
        created: "2025-01-10T10:00:00Z",
        lastUsed: "2025-01-11T14:30:00Z",
    },
    {
        id: "key-2",
        name: "Development Key",
        prefix: "sk_test_",
        created: "2025-01-08T09:00:00Z",
        lastUsed: "2025-01-11T12:00:00Z",
    },
];

const quickLinks = [
    { icon: <Book className="w-5 h-5" />, title: "API Documentation", description: "Complete API reference", href: "/docs/api" },
    { icon: <Code2 className="w-5 h-5" />, title: "Quick Start Guide", description: "Get started in 5 minutes", href: "/docs/quickstart" },
    { icon: <Settings className="w-5 h-5" />, title: "Webhooks", description: "Real-time event notifications", href: "/docs/webhooks" },
];

export default function DevelopersPage() {
    const [apiKeys] = React.useState(mockApiKeys);
    const [visibleKeys, setVisibleKeys] = React.useState<Set<string>>(new Set());
    const [showCreateModal, setShowCreateModal] = React.useState(false);

    const toggleKeyVisibility = (keyId: string) => {
        const newVisible = new Set(visibleKeys);
        if (newVisible.has(keyId)) {
            newVisible.delete(keyId);
        } else {
            newVisible.add(keyId);
        }
        setVisibleKeys(newVisible);
    };

    const maskKey = (prefix: string) => `${prefix}${"•".repeat(32)}`;

    return (
        <div className="max-w-full">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">Developers</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Manage API keys and access developer resources
                    </p>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    Create API Key
                </button>
            </div>

            {/* API Keys Section */}
            <div className="bg-white border border-gray-200 rounded-lg mb-6">
                <div className="px-4 py-3 border-b border-gray-200">
                    <h2 className="font-medium text-gray-900">API Keys</h2>
                </div>
                <div className="divide-y divide-gray-100">
                    {apiKeys.map((key) => (
                        <div key={key.id} className="px-4 py-4 flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
                                    <Key className="w-5 h-5 text-gray-500" />
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900">{key.name}</h3>
                                    <div className="flex items-center gap-2 mt-1">
                                        <code className="text-sm text-gray-600 font-mono bg-gray-100 px-2 py-0.5 rounded">
                                            {visibleKeys.has(key.id) ? `${key.prefix}abc123xyz456...` : maskKey(key.prefix)}
                                        </code>
                                        <button
                                            onClick={() => toggleKeyVisibility(key.id)}
                                            className="text-gray-400 hover:text-gray-600"
                                        >
                                            {visibleKeys.has(key.id) ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                        </button>
                                        <button className="text-gray-400 hover:text-gray-600">
                                            <Copy className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="text-right text-sm">
                                    <p className="text-gray-500">Last used</p>
                                    <p className="text-gray-900">{new Date(key.lastUsed).toLocaleDateString()}</p>
                                </div>
                                <div className="flex items-center gap-1">
                                    <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                                        <RefreshCw className="w-4 h-4" />
                                    </button>
                                    <button className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg">
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Quick Links */}
            <h2 className="font-medium text-gray-900 mb-4">Developer Resources</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {quickLinks.map((link) => (
                    <Link
                        key={link.title}
                        href={link.href}
                        className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-all group"
                    >
                        <div className="flex items-start gap-3">
                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                {link.icon}
                            </div>
                            <div className="flex-1">
                                <h3 className="font-medium text-gray-900 group-hover:text-blue-600 transition-colors flex items-center gap-1">
                                    {link.title}
                                    <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                                </h3>
                                <p className="text-sm text-gray-500 mt-1">{link.description}</p>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>

            {/* Create API Key Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl max-w-md w-full">
                        <div className="flex items-center justify-between p-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Create API Key</h3>
                            <button onClick={() => setShowCreateModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Key Name</label>
                                <input
                                    type="text"
                                    placeholder="e.g. Production API Key"
                                    className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Environment</label>
                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                    <option>Production</option>
                                    <option>Development</option>
                                </select>
                            </div>
                        </div>
                        <div className="flex justify-end gap-3 p-4 border-t border-gray-200">
                            <button onClick={() => setShowCreateModal(false)} className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                                Cancel
                            </button>
                            <button className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg">
                                Create Key
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
