/**
 * Tools Configuration Page
 * Function calling and webhook management
 */
"use client";

import * as React from "react";
import { motion } from "framer-motion";
import {
    Wrench,
    Plus,
    Code,
    Webhook,
    Trash2,
    Edit,
    Play,
    Check,
    X,
    Copy,
    Settings,
    Globe,
    Zap,
    Calendar,
    Calculator,
    Database,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// Built-in tools
const builtInTools = [
    {
        id: "calendar",
        name: "Calendar Integration",
        description: "Book appointments and check availability",
        icon: Calendar,
        enabled: true,
    },
    {
        id: "calculator",
        name: "Calculator",
        description: "Perform calculations during calls",
        icon: Calculator,
        enabled: true,
    },
    {
        id: "knowledge_base",
        name: "Knowledge Base",
        description: "Query uploaded documents for answers",
        icon: Database,
        enabled: true,
    },
    {
        id: "web_search",
        name: "Web Search",
        description: "Search the web for current information",
        icon: Globe,
        enabled: false,
    },
    {
        id: "crm",
        name: "CRM Integration",
        description: "Look up and update customer records",
        icon: Database,
        enabled: false,
    },
];

// Custom functions
const mockCustomFunctions = [
    {
        id: "func_001",
        name: "check_inventory",
        description: "Check product inventory levels",
        endpoint: "https://api.example.com/inventory",
        method: "GET",
        lastUsed: "2 hours ago",
    },
    {
        id: "func_002",
        name: "create_ticket",
        description: "Create a support ticket",
        endpoint: "https://api.example.com/tickets",
        method: "POST",
        lastUsed: "1 day ago",
    },
];

export default function ToolsPage() {
    const [tools, setTools] = React.useState(builtInTools);
    const [showAddModal, setShowAddModal] = React.useState(false);
    const [newFunction, setNewFunction] = React.useState({
        name: "",
        description: "",
        endpoint: "",
        method: "GET",
    });

    const toggleTool = (id: string) => {
        setTools(tools.map((tool) =>
            tool.id === id ? { ...tool, enabled: !tool.enabled } : tool
        ));
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">Tools & Functions</h1>
                    <p className="text-gray-400 mt-1">
                        Configure function calling and external integrations
                    </p>
                </div>
                <Button
                    leftIcon={<Plus className="h-4 w-4" />}
                    onClick={() => setShowAddModal(true)}
                >
                    Add Custom Function
                </Button>
            </div>

            {/* Built-in Tools */}
            <Card variant="default">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Zap className="h-5 w-5 text-purple-400" />
                        Built-in Tools
                    </CardTitle>
                    <CardDescription>
                        Enable or disable built-in capabilities for your agents
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {tools.map((tool) => (
                            <div
                                key={tool.id}
                                className="flex items-center justify-between p-4 rounded-lg bg-[#1A1A2E]"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="p-2 rounded-lg bg-purple-500/10">
                                        <tool.icon className="h-5 w-5 text-purple-400" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-white">{tool.name}</p>
                                        <p className="text-sm text-gray-500">{tool.description}</p>
                                    </div>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={tool.enabled}
                                        onChange={() => toggleTool(tool.id)}
                                        className="sr-only peer"
                                    />
                                    <div className="w-11 h-6 bg-[#374151] peer-focus:ring-2 peer-focus:ring-purple-500/20 rounded-full peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-500"></div>
                                </label>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Custom Functions */}
            <Card variant="default">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Code className="h-5 w-5 text-blue-400" />
                        Custom Functions
                    </CardTitle>
                    <CardDescription>
                        Define custom API endpoints for your agents to call
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {mockCustomFunctions.length === 0 ? (
                        <div className="text-center py-8">
                            <Wrench className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                            <p className="text-gray-400 mb-4">No custom functions defined</p>
                            <Button onClick={() => setShowAddModal(true)}>
                                Add Function
                            </Button>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {mockCustomFunctions.map((func) => (
                                <div
                                    key={func.id}
                                    className="flex items-center justify-between p-4 rounded-lg bg-[#1A1A2E]"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="p-2 rounded-lg bg-blue-500/10">
                                            <Webhook className="h-5 w-5 text-blue-400" />
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <code className="font-medium text-white">{func.name}</code>
                                                <Badge variant={func.method === "GET" ? "info" : "success"} size="sm">
                                                    {func.method}
                                                </Badge>
                                            </div>
                                            <p className="text-sm text-gray-500">{func.description}</p>
                                            <p className="text-xs text-gray-600 font-mono mt-1">{func.endpoint}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <span className="text-xs text-gray-500">Used {func.lastUsed}</span>
                                        <div className="flex items-center gap-2">
                                            <button className="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-[#252540] transition-colors">
                                                <Play className="h-4 w-4" />
                                            </button>
                                            <button className="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-[#252540] transition-colors">
                                                <Edit className="h-4 w-4" />
                                            </button>
                                            <button className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors">
                                                <Trash2 className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Webhook Configuration */}
            <Card variant="default">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Globe className="h-5 w-5 text-emerald-400" />
                        Webhook Settings
                    </CardTitle>
                    <CardDescription>
                        Receive real-time events for calls and agent activity
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <Input
                        label="Webhook URL"
                        placeholder="https://your-server.com/webhook"
                        leftIcon={<Webhook className="h-4 w-4" />}
                    />

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">
                            Event Types
                        </label>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                            {[
                                "call.started",
                                "call.ended",
                                "call.failed",
                                "agent.created",
                                "agent.updated",
                                "transcription.ready",
                            ].map((event) => (
                                <label
                                    key={event}
                                    className="flex items-center gap-2 p-2 rounded-lg bg-[#1A1A2E] cursor-pointer"
                                >
                                    <input
                                        type="checkbox"
                                        defaultChecked={event.startsWith("call")}
                                        className="rounded border-[#374151] bg-[#252540] text-purple-500"
                                    />
                                    <code className="text-sm text-gray-300">{event}</code>
                                </label>
                            ))}
                        </div>
                    </div>

                    <Button>Save Webhook Settings</Button>
                </CardContent>
            </Card>

            {/* Add Function Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="w-full max-w-lg"
                    >
                        <Card variant="elevated">
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle>Add Custom Function</CardTitle>
                                <button
                                    onClick={() => setShowAddModal(false)}
                                    className="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-[#252540] transition-colors"
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <Input
                                    label="Function Name"
                                    placeholder="e.g., check_inventory"
                                    value={newFunction.name}
                                    onChange={(e) => setNewFunction({ ...newFunction, name: e.target.value })}
                                />
                                <Input
                                    label="Description"
                                    placeholder="What does this function do?"
                                    value={newFunction.description}
                                    onChange={(e) => setNewFunction({ ...newFunction, description: e.target.value })}
                                />
                                <Input
                                    label="Endpoint URL"
                                    placeholder="https://api.example.com/endpoint"
                                    value={newFunction.endpoint}
                                    onChange={(e) => setNewFunction({ ...newFunction, endpoint: e.target.value })}
                                    leftIcon={<Globe className="h-4 w-4" />}
                                />
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        HTTP Method
                                    </label>
                                    <div className="flex gap-2">
                                        {["GET", "POST", "PUT", "DELETE"].map((method) => (
                                            <button
                                                key={method}
                                                onClick={() => setNewFunction({ ...newFunction, method })}
                                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${newFunction.method === method
                                                        ? "bg-purple-500 text-white"
                                                        : "bg-[#252540] text-gray-400 hover:text-white"
                                                    }`}
                                            >
                                                {method}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="flex gap-3 pt-4">
                                    <Button
                                        variant="outline"
                                        className="flex-1"
                                        onClick={() => setShowAddModal(false)}
                                    >
                                        Cancel
                                    </Button>
                                    <Button className="flex-1" leftIcon={<Plus className="h-4 w-4" />}>
                                        Add Function
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </motion.div>
                </div>
            )}
        </div>
    );
}
