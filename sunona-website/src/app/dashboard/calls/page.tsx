/**
 * Calls Page - Agent Conversations - Light Theme
 * Performance metrics and call history
 */
"use client";

import * as React from "react";
import {
    PhoneCall,
    Search,
    Download,
    RefreshCw,
    Clock,
    DollarSign,
    BarChart3,
    Calendar,
    ChevronDown,
    Play,
    FileText,
    PhoneIncoming,
    PhoneOutgoing,
} from "lucide-react";

// Mock call data
const mockCalls = [
    {
        callId: "call_abc123def456",
        phoneNumber: "+918123456789",
        direction: "outbound",
        durationSeconds: 145,
        summary: "Customer inquired about product pricing and delivery options",
        status: "completed",
        cost: 0.24,
        startedAt: "2025-01-11T10:30:00Z",
        agentName: "Customer Support Agent",
        hangupBy: "user",
    },
    {
        callId: "call_xyz789ghi012",
        phoneNumber: "+919876543210",
        direction: "inbound",
        durationSeconds: 89,
        summary: "Support ticket created for order tracking",
        status: "completed",
        cost: 0.15,
        startedAt: "2025-01-11T09:15:00Z",
        agentName: "Sales Outreach Agent",
        hangupBy: "agent",
    },
    {
        callId: "call_mno345pqr678",
        phoneNumber: "+917654321098",
        direction: "outbound",
        durationSeconds: 0,
        summary: "",
        status: "no-answer",
        cost: 0.01,
        startedAt: "2025-01-11T08:45:00Z",
        agentName: "Appointment Booking Agent",
        hangupBy: "-",
    },
];

export default function CallsPage() {
    const [calls] = React.useState(mockCalls);
    const [search, setSearch] = React.useState("");
    const [filter, setFilter] = React.useState<"all" | "inbound" | "outbound">("all");
    const [dateRange] = React.useState("Jan 01, 2025 - Jan 11, 2025");
    const [activeTab, setActiveTab] = React.useState<"conversation" | "trace" | "raw">("conversation");

    const filteredCalls = React.useMemo(() => {
        return calls.filter((call) => {
            if (filter !== "all" && call.direction !== filter) return false;
            if (search && !call.phoneNumber?.includes(search) && !call.callId?.includes(search)) return false;
            return true;
        });
    }, [calls, search, filter]);

    // Calculate metrics
    const metrics = React.useMemo(() => {
        const totalCost = filteredCalls.reduce((acc, call) => acc + (call.cost || 0), 0);
        const totalDuration = filteredCalls.reduce((acc, call) => acc + (call.durationSeconds || 0), 0);
        const avgCost = filteredCalls.length > 0 ? totalCost / filteredCalls.length : 0;
        const avgDuration = filteredCalls.length > 0 ? totalDuration / filteredCalls.length : 0;

        return {
            totalExecutions: filteredCalls.length,
            totalCost,
            totalDuration,
            avgCost,
            avgDuration,
        };
    }, [filteredCalls]);

    const formatDuration = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <div className="max-w-full">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">Agent Conversations</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Displays all historical conversations with agents
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                        <RefreshCw className="w-4 h-4" />
                        Refresh
                    </button>
                    <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                        <Download className="w-4 h-4" />
                        Download records
                    </button>
                </div>
            </div>

            {/* Filters Row */}
            <div className="flex items-center gap-4 mb-6">
                {/* Agent Filter */}
                <div className="relative">
                    <select
                        className="appearance-none px-4 py-2.5 pr-10 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
                    >
                        <option value="all">Choose agent...</option>
                        <option value="agent1">Customer Support Agent</option>
                        <option value="agent2">Sales Outreach Agent</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>

                {/* Batch Filter */}
                <div className="relative">
                    <select
                        className="appearance-none px-4 py-2.5 pr-10 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer"
                    >
                        <option value="all">Choose batch...</option>
                        <option value="batch1">Batch 1</option>
                        <option value="batch2">Batch 2</option>
                    </select>
                    <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>

                {/* Date Range */}
                <div className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-300 rounded-lg">
                    <Calendar className="w-4 h-4 text-blue-600" />
                    <span className="text-sm text-gray-900">{dateRange}</span>
                </div>
            </div>

            {/* Performance Metrics */}
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-4">
                    <BarChart3 className="w-4 h-4 text-blue-600" />
                    <h2 className="text-sm font-medium text-gray-900">Performance Metrics</h2>
                </div>

                <div className="grid grid-cols-5 gap-4">
                    {/* Total Executions */}
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs text-gray-500">Total Executions</span>
                            <PhoneCall className="w-4 h-4 text-blue-600" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900">{metrics.totalExecutions}</p>
                        <p className="text-xs text-gray-500 mt-1">All call attempts</p>
                    </div>

                    {/* Total Cost */}
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs text-gray-500">Total Cost</span>
                            <DollarSign className="w-4 h-4 text-blue-600" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900">${metrics.totalCost.toFixed(2)}</p>
                        <p className="text-xs text-gray-500 mt-1">Total campaign spend</p>
                    </div>

                    {/* Total Duration */}
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs text-gray-500">Total Duration</span>
                            <Clock className="w-4 h-4 text-blue-600" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900">{formatDuration(metrics.totalDuration)}</p>
                        <p className="text-xs text-gray-500 mt-1">Total call time</p>
                    </div>

                    {/* Avg Cost */}
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs text-gray-500">Avg Cost</span>
                            <DollarSign className="w-4 h-4 text-blue-600" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900">${metrics.avgCost.toFixed(2)}</p>
                        <p className="text-xs text-gray-500 mt-1">Per call average</p>
                    </div>

                    {/* Avg Duration */}
                    <div className="bg-white border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs text-gray-500">Avg Duration</span>
                            <Clock className="w-4 h-4 text-blue-600" />
                        </div>
                        <p className="text-2xl font-bold text-gray-900">{formatDuration(Math.round(metrics.avgDuration))}</p>
                        <p className="text-xs text-gray-500 mt-1">Per call average</p>
                    </div>
                </div>
            </div>

            {/* Search & Tabs */}
            <div className="flex items-center justify-between mb-4">
                <div className="relative flex-1 max-w-sm">
                    <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none" style={{ paddingLeft: '14px' }}>
                        <Search className="w-4 h-4 text-gray-400" />
                    </div>
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search by Execution ID or phone number"
                        style={{ paddingLeft: '40px' }}
                        className="w-full pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all duration-200"
                    />
                </div>




                <div className="flex border border-gray-200 rounded-lg overflow-hidden">
                    {(["conversation", "trace", "raw"] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`px-4 py-2 text-sm capitalize transition-colors ${activeTab === tab
                                ? "bg-blue-50 text-blue-600"
                                : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                                }`}
                        >
                            {tab}
                        </button>
                    ))}
                </div>
            </div>

            {/* Calls Table */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                {/* Table Header */}
                <div className="grid grid-cols-9 gap-2 px-4 py-3 bg-gray-50 border-b border-gray-200 text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <div>Execution</div>
                    <div>User</div>
                    <div className="col-span-2">Conversation</div>
                    <div>Duration</div>
                    <div>Hangup by</div>
                    <div>Timestamp</div>
                    <div>Cost</div>
                    <div>Status</div>
                </div>

                {/* Table Body */}
                {filteredCalls.length > 0 ? (
                    <div className="divide-y divide-gray-100">
                        {filteredCalls.map((call) => (
                            <div
                                key={call.callId}
                                className="grid grid-cols-9 gap-2 px-4 py-3 items-center text-sm hover:bg-gray-50 transition-colors cursor-pointer group"
                            >
                                <div className="flex items-center gap-2">
                                    {call.direction === "inbound" ? (
                                        <PhoneIncoming className="w-4 h-4 text-emerald-500" />
                                    ) : (
                                        <PhoneOutgoing className="w-4 h-4 text-blue-500" />
                                    )}
                                    <span className="font-mono text-xs text-gray-500 truncate">
                                        {call.callId?.slice(0, 12)}...
                                    </span>
                                </div>
                                <div className="text-gray-900 truncate">{call.phoneNumber}</div>
                                <div className="col-span-2 text-gray-600 truncate">
                                    {call.summary || "No summary available"}
                                </div>
                                <div className="text-gray-900">{formatDuration(call.durationSeconds)}</div>
                                <div className="text-gray-500 capitalize">{call.hangupBy}</div>
                                <div className="text-xs text-gray-500">
                                    {new Date(call.startedAt).toLocaleString('en-US', {
                                        month: 'short',
                                        day: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit'
                                    })}
                                </div>
                                <div className="font-mono text-gray-900">${call.cost.toFixed(3)}</div>
                                <div className="flex items-center gap-2">
                                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${call.status === "completed"
                                        ? "bg-emerald-100 text-emerald-700"
                                        : call.status === "no-answer"
                                            ? "bg-amber-100 text-amber-700"
                                            : "bg-gray-100 text-gray-600"
                                        }`}>
                                        {call.status}
                                    </span>
                                    <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                                        <button className="p-1 rounded hover:bg-gray-200 text-gray-400 hover:text-blue-600">
                                            <Play className="w-3 h-3" />
                                        </button>
                                        <button className="p-1 rounded hover:bg-gray-200 text-gray-400 hover:text-blue-600">
                                            <FileText className="w-3 h-3" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-16">
                        <PhoneCall className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p className="text-sm text-gray-600">No calls found</p>
                        <p className="text-xs text-gray-400 mt-1">
                            Make your first call to see it here
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
