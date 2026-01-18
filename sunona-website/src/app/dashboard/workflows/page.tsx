/**
 * Workflows Page - Light Theme
 * Manage agent workflows
 */
"use client";

import * as React from "react";
import {
    Workflow,
    Plus,
    Search,
    Play,
    Pause,
    Trash2,
    Edit,
    Copy,
    MoreHorizontal,
} from "lucide-react";

const mockWorkflows = [
    {
        id: "wf-1",
        name: "Customer Support Flow",
        description: "Handle incoming customer queries with escalation",
        status: "active",
        lastRun: "2025-01-11T10:30:00Z",
        runs: 156,
    },
    {
        id: "wf-2",
        name: "Lead Qualification",
        description: "Qualify and route inbound leads",
        status: "active",
        lastRun: "2025-01-11T09:15:00Z",
        runs: 89,
    },
    {
        id: "wf-3",
        name: "Appointment Reminder",
        description: "Send automated appointment reminders",
        status: "paused",
        lastRun: "2025-01-10T16:00:00Z",
        runs: 234,
    },
];

export default function WorkflowsPage() {
    const [workflows] = React.useState(mockWorkflows);
    const [search, setSearch] = React.useState("");

    return (
        <div className="max-w-full">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">Workflows</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Create and manage automated agent workflows
                    </p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
                    <Plus className="w-4 h-4" />
                    Create Workflow
                </button>
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
                    placeholder="Search workflows..."
                    style={{ paddingLeft: '40px' }}
                    className="w-full pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all duration-200"
                />
            </div>






            {/* Workflows List */}
            <div className="space-y-3">
                {workflows.map((workflow) => (
                    <div
                        key={workflow.id}
                        className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                    >
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                    <Workflow className="w-5 h-5 text-blue-600" />
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900">{workflow.name}</h3>
                                    <p className="text-sm text-gray-500">{workflow.description}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="text-right text-sm">
                                    <p className="text-gray-900">{workflow.runs} runs</p>
                                    <p className="text-gray-500">Last: {new Date(workflow.lastRun).toLocaleDateString()}</p>
                                </div>
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${workflow.status === "active"
                                    ? "bg-emerald-100 text-emerald-700"
                                    : "bg-amber-100 text-amber-700"
                                    }`}>
                                    {workflow.status}
                                </span>
                                <div className="flex items-center gap-1">
                                    <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                                        <Edit className="w-4 h-4" />
                                    </button>
                                    <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                                        <Copy className="w-4 h-4" />
                                    </button>
                                    <button className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg">
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {workflows.length === 0 && (
                <div className="text-center py-16 bg-white border border-gray-200 rounded-lg">
                    <Workflow className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-sm text-gray-600">No workflows created yet</p>
                    <p className="text-xs text-gray-400 mt-1">Create your first workflow to automate tasks</p>
                </div>
            )}
        </div>
    );
}
