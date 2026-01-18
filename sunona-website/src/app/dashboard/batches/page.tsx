/**
 * Batches Page - Light Theme
 * Manage batch calling campaigns
 */
"use client";

import * as React from "react";
import Link from "next/link";
import {
    Layers,
    Search,
    Upload,
    Download,
    Play,
    Pause,
    CheckCircle,
    Clock,
    AlertCircle,
    ChevronDown,
    Trash2,
    Eye,
    X,
} from "lucide-react";

// Mock batches data
const mockBatches = [
    {
        id: "batch-1",
        name: "Q1 Sales Outreach",
        agent: "Sales Agent",
        status: "completed",
        totalCalls: 500,
        completed: 500,
        successful: 423,
        failed: 77,
        createdAt: "2025-01-10T10:00:00Z",
        cost: 45.50,
    },
    {
        id: "batch-2",
        name: "Customer Feedback Survey",
        agent: "Survey Agent",
        status: "in-progress",
        totalCalls: 1000,
        completed: 342,
        successful: 298,
        failed: 44,
        createdAt: "2025-01-11T08:00:00Z",
        cost: 28.90,
    },
    {
        id: "batch-3",
        name: "COD Confirmation",
        agent: "COD Agent",
        status: "paused",
        totalCalls: 300,
        completed: 89,
        successful: 76,
        failed: 13,
        createdAt: "2025-01-09T15:00:00Z",
        cost: 8.90,
    },
];

export default function BatchesPage() {
    const [batches] = React.useState(mockBatches);
    const [search, setSearch] = React.useState("");
    const [showUploadModal, setShowUploadModal] = React.useState(false);

    const getStatusBadge = (status: string) => {
        switch (status) {
            case "completed":
                return (
                    <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-emerald-100 text-emerald-700 rounded-full">
                        <CheckCircle className="w-3 h-3" />
                        Completed
                    </span>
                );
            case "in-progress":
                return (
                    <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-blue-100 text-blue-700 rounded-full">
                        <Play className="w-3 h-3" />
                        In Progress
                    </span>
                );
            case "paused":
                return (
                    <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-amber-100 text-amber-700 rounded-full">
                        <Pause className="w-3 h-3" />
                        Paused
                    </span>
                );
            case "failed":
                return (
                    <span className="flex items-center gap-1 px-2 py-1 text-xs font-medium bg-red-100 text-red-700 rounded-full">
                        <AlertCircle className="w-3 h-3" />
                        Failed
                    </span>
                );
            default:
                return null;
        }
    };

    const getProgress = (completed: number, total: number) => ((completed / total) * 100).toFixed(0);

    return (
        <div className="max-w-full">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">Agent Batches</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Manage your batch calling campaigns
                    </p>
                </div>
            </div>

            {/* Filters & Actions */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-4">
                    {/* Agent Filter */}
                    <div className="relative">
                        <select className="appearance-none px-4 py-2.5 pr-10 bg-white border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer">
                            <option>Choose agent...</option>
                            <option>Sales Agent</option>
                            <option>Survey Agent</option>
                            <option>COD Agent</option>
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                    </div>

                    <Link href="#" className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1">
                        <Download className="w-4 h-4" />
                        Download template
                    </Link>
                </div>

                <button
                    onClick={() => setShowUploadModal(true)}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                >
                    <Upload className="w-4 h-4" />
                    Upload Batch
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
                    placeholder="Search batches..."
                    style={{ paddingLeft: '40px' }}
                    className="w-full pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all duration-200"
                />
            </div>




            {/* Batches Table */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="bg-gray-50 border-b border-gray-200">
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Batch Name</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Agent</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Progress</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Success Rate</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Cost</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Status</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {batches.map((batch) => (
                            <tr key={batch.id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <Layers className="w-4 h-4 text-blue-600" />
                                        <span className="font-medium text-gray-900">{batch.name}</span>
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-600">{batch.agent}</td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <div className="flex-1 max-w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-blue-600 rounded-full"
                                                style={{ width: `${getProgress(batch.completed, batch.totalCalls)}%` }}
                                            />
                                        </div>
                                        <span className="text-xs text-gray-600">{batch.completed}/{batch.totalCalls}</span>
                                    </div>
                                </td>
                                <td className="px-4 py-3">
                                    <span className="text-sm text-gray-900">
                                        {((batch.successful / batch.completed) * 100).toFixed(1)}%
                                    </span>
                                </td>
                                <td className="px-4 py-3">
                                    <span className="font-mono text-sm text-gray-900">${batch.cost.toFixed(2)}</span>
                                </td>
                                <td className="px-4 py-3">{getStatusBadge(batch.status)}</td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <button className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded">
                                            <Eye className="w-4 h-4" />
                                        </button>
                                        {batch.status === "in-progress" ? (
                                            <button className="p-1.5 text-gray-400 hover:text-amber-600 hover:bg-amber-50 rounded">
                                                <Pause className="w-4 h-4" />
                                            </button>
                                        ) : batch.status === "paused" ? (
                                            <button className="p-1.5 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded">
                                                <Play className="w-4 h-4" />
                                            </button>
                                        ) : null}
                                        <button className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {batches.length === 0 && (
                    <div className="text-center py-16">
                        <Layers className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p className="text-sm text-gray-600">No batches created yet</p>
                        <p className="text-xs text-gray-400 mt-1">Upload a CSV to create your first batch</p>
                    </div>
                )}
            </div>

            {/* Upload Modal */}
            {showUploadModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl max-w-md w-full">
                        <div className="flex items-center justify-between p-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Upload Batch</h3>
                            <button onClick={() => setShowUploadModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Agent</label>
                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                    <option>Select agent...</option>
                                    <option>Sales Agent</option>
                                    <option>Survey Agent</option>
                                </select>
                            </div>
                            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors cursor-pointer">
                                <Upload className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                                <p className="text-sm text-gray-600">Drop your CSV here</p>
                            </div>
                        </div>
                        <div className="flex justify-end gap-3 p-4 border-t border-gray-200">
                            <button onClick={() => setShowUploadModal(false)} className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                                Cancel
                            </button>
                            <button className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg">
                                Upload
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
