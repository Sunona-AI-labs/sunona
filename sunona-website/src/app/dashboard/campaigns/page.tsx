/**
 * Campaigns Page - Light Theme
 * Manage calling campaigns
 */
"use client";

import * as React from "react";
import {
    Megaphone,
    Plus,
    Search,
    Play,
    Pause,
    Trash2,
    Edit,
    BarChart3,
    Phone,
    CheckCircle,
} from "lucide-react";

const mockCampaigns = [
    {
        id: "camp-1",
        name: "Q1 Sales Campaign",
        agent: "Sales Agent",
        status: "active",
        totalLeads: 1500,
        contacted: 890,
        converted: 234,
        startDate: "2025-01-01",
        endDate: "2025-03-31",
    },
    {
        id: "camp-2",
        name: "Customer Feedback 2025",
        agent: "Survey Agent",
        status: "active",
        totalLeads: 500,
        contacted: 156,
        converted: 89,
        startDate: "2025-01-10",
        endDate: "2025-01-31",
    },
    {
        id: "camp-3",
        name: "Product Launch Outreach",
        agent: "Marketing Agent",
        status: "scheduled",
        totalLeads: 2000,
        contacted: 0,
        converted: 0,
        startDate: "2025-02-01",
        endDate: "2025-02-28",
    },
];

export default function CampaignsPage() {
    const [campaigns] = React.useState(mockCampaigns);
    const [search, setSearch] = React.useState("");

    const getProgress = (contacted: number, total: number) => ((contacted / total) * 100).toFixed(0);

    return (
        <div className="max-w-full">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">Campaigns</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Create and manage calling campaigns
                    </p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
                    <Plus className="w-4 h-4" />
                    Create Campaign
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
                    placeholder="Search campaigns..."
                    style={{ paddingLeft: '40px' }}
                    className="w-full pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all duration-200"
                />
            </div>




            {/* Campaigns Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {campaigns.map((campaign) => (
                    <div
                        key={campaign.id}
                        className="bg-white border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                    >
                        <div className="flex items-start justify-between mb-3">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                                    <Megaphone className="w-5 h-5 text-purple-600" />
                                </div>
                                <div>
                                    <h3 className="font-medium text-gray-900">{campaign.name}</h3>
                                    <p className="text-xs text-gray-500">{campaign.agent}</p>
                                </div>
                            </div>
                            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${campaign.status === "active"
                                ? "bg-emerald-100 text-emerald-700"
                                : "bg-blue-100 text-blue-700"
                                }`}>
                                {campaign.status}
                            </span>
                        </div>

                        {/* Progress */}
                        <div className="mb-3">
                            <div className="flex items-center justify-between text-xs mb-1">
                                <span className="text-gray-500">Progress</span>
                                <span className="text-gray-900">{campaign.contacted}/{campaign.totalLeads}</span>
                            </div>
                            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-blue-600 rounded-full"
                                    style={{ width: `${getProgress(campaign.contacted, campaign.totalLeads)}%` }}
                                />
                            </div>
                        </div>

                        {/* Stats */}
                        <div className="flex items-center gap-4 text-sm mb-3">
                            <div className="flex items-center gap-1 text-gray-600">
                                <Phone className="w-3.5 h-3.5" />
                                {campaign.contacted} calls
                            </div>
                            <div className="flex items-center gap-1 text-emerald-600">
                                <CheckCircle className="w-3.5 h-3.5" />
                                {campaign.converted} converted
                            </div>
                        </div>

                        {/* Date Range */}
                        <div className="text-xs text-gray-500 mb-3">
                            {campaign.startDate} → {campaign.endDate}
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2">
                            <button className="flex-1 flex items-center justify-center gap-1 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                                <BarChart3 className="w-4 h-4" />
                                Analytics
                            </button>
                            <button className="flex-1 flex items-center justify-center gap-1 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                                <Edit className="w-4 h-4" />
                                Edit
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {campaigns.length === 0 && (
                <div className="text-center py-16 bg-white border border-gray-200 rounded-lg">
                    <Megaphone className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p className="text-sm text-gray-600">No campaigns created yet</p>
                    <p className="text-xs text-gray-400 mt-1">Create a campaign to start outreach</p>
                </div>
            )}
        </div>
    );
}
