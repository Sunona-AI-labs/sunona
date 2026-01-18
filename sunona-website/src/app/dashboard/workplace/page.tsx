/**
 * Workplace Settings Page - Sunona Dark Industrial AI Theme
 * Team management and workspace settings
 */
"use client";

import * as React from "react";
import {
    Settings,
    Users,
    Shield,
    Bell,
    Webhook,
    Plus,
    Trash2,
    Edit2,
    Mail,
    Crown,
    CheckCircle,
    Clock,
    Copy,
    ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";

// Tabs
const settingsTabs = [
    { id: "team", label: "Team Members", icon: <Users className="w-4 h-4" /> },
    { id: "roles", label: "Roles & Permissions", icon: <Shield className="w-4 h-4" /> },
    { id: "notifications", label: "Notifications", icon: <Bell className="w-4 h-4" /> },
    { id: "webhooks", label: "Webhooks", icon: <Webhook className="w-4 h-4" /> },
];

// Mock team members
const teamMembers = [
    { id: "user-1", name: "John Doe", email: "john@company.com", role: "Owner", status: "active", avatar: "JD" },
    { id: "user-2", name: "Jane Smith", email: "jane@company.com", role: "Admin", status: "active", avatar: "JS" },
    { id: "user-3", name: "Mike Johnson", email: "mike@company.com", role: "Member", status: "active", avatar: "MJ" },
    { id: "user-4", name: "Sarah Wilson", email: "sarah@company.com", role: "Member", status: "pending", avatar: "SW" },
];

// Mock webhooks
const webhooks = [
    { id: "wh-1", name: "Call Completed", url: "https://api.company.com/webhooks/calls", events: ["call.completed", "call.failed"], active: true },
    { id: "wh-2", name: "Agent Updates", url: "https://api.company.com/webhooks/agents", events: ["agent.created", "agent.updated"], active: true },
];

export default function WorkplacePage() {
    const [activeTab, setActiveTab] = React.useState("team");

    return (
        <div className="max-w-4xl">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-white">Workplace Settings</h1>
                    <p className="text-sm text-[#B0B0B0] mt-1">
                        Manage your team and workspace configuration
                    </p>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-white/10 mb-6">
                {settingsTabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === tab.id
                                ? "border-[#00D4AA] text-[#00D4AA]"
                                : "border-transparent text-[#6B6B6B] hover:text-white"
                            }`}
                    >
                        {tab.icon}
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === "team" && (
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-medium text-white">Team Members</h2>
                        <Button size="sm">
                            <Plus className="w-4 h-4 mr-2" />
                            Invite Member
                        </Button>
                    </div>

                    <div className="bg-[#111111] border border-white/10 rounded-lg overflow-hidden">
                        <div className="divide-y divide-white/5">
                            {teamMembers.map((member) => (
                                <div
                                    key={member.id}
                                    className="flex items-center justify-between p-4 hover:bg-white/5 transition-colors group"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#00D4AA] to-[#00F5C8] flex items-center justify-center text-black font-medium text-sm">
                                            {member.avatar}
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <p className="text-white font-medium">{member.name}</p>
                                                {member.role === "Owner" && (
                                                    <Crown className="w-4 h-4 text-[#FFB347]" />
                                                )}
                                            </div>
                                            <p className="text-sm text-[#6B6B6B]">{member.email}</p>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-4">
                                        <span className={`px-2 py-1 text-xs rounded-full ${member.role === "Owner"
                                                ? "bg-[#FFB347]/10 text-[#FFB347]"
                                                : member.role === "Admin"
                                                    ? "bg-[#9B59B6]/10 text-[#9B59B6]"
                                                    : "bg-white/5 text-[#B0B0B0]"
                                            }`}>
                                            {member.role}
                                        </span>
                                        {member.status === "pending" ? (
                                            <span className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-[#FFB347]/10 text-[#FFB347] rounded-full">
                                                <Clock className="w-3 h-3" />
                                                Pending
                                            </span>
                                        ) : (
                                            <span className="inline-flex items-center gap-1 px-2 py-1 text-xs bg-[#00D4AA]/10 text-[#00D4AA] rounded-full">
                                                <CheckCircle className="w-3 h-3" />
                                                Active
                                            </span>
                                        )}
                                        <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                                            <button className="p-2 rounded-lg text-[#6B6B6B] hover:text-white hover:bg-white/5">
                                                <Edit2 className="w-4 h-4" />
                                            </button>
                                            {member.role !== "Owner" && (
                                                <button className="p-2 rounded-lg text-[#6B6B6B] hover:text-[#FF4757] hover:bg-[#FF4757]/10">
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {activeTab === "roles" && (
                <div>
                    <h2 className="text-lg font-medium text-white mb-4">Roles & Permissions</h2>
                    <div className="space-y-4">
                        {["Owner", "Admin", "Member"].map((role) => (
                            <div
                                key={role}
                                className="bg-[#111111] border border-white/10 rounded-lg p-5"
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center gap-2">
                                        <h3 className="font-medium text-white">{role}</h3>
                                        {role === "Owner" && <Crown className="w-4 h-4 text-[#FFB347]" />}
                                    </div>
                                    {role !== "Owner" && (
                                        <Button variant="ghost" size="sm">
                                            <Edit2 className="w-3 h-3 mr-1" />
                                            Edit
                                        </Button>
                                    )}
                                </div>
                                <div className="grid grid-cols-4 gap-2">
                                    {["Agents", "Calls", "Billing", "Team"].map((perm) => (
                                        <div
                                            key={perm}
                                            className={`px-3 py-2 rounded text-xs text-center ${role === "Owner" || (role === "Admin" && perm !== "Billing")
                                                    ? "bg-[#00D4AA]/10 text-[#00D4AA]"
                                                    : role === "Member" && ["Agents", "Calls"].includes(perm)
                                                        ? "bg-[#00D4AA]/10 text-[#00D4AA]"
                                                        : "bg-white/5 text-[#6B6B6B]"
                                                }`}
                                        >
                                            {perm}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {activeTab === "notifications" && (
                <div>
                    <h2 className="text-lg font-medium text-white mb-4">Notification Preferences</h2>
                    <div className="bg-[#111111] border border-white/10 rounded-lg divide-y divide-white/5">
                        {[
                            { label: "Call completed", description: "Get notified when a call is completed" },
                            { label: "Low balance alert", description: "Alert when wallet balance is low" },
                            { label: "Agent errors", description: "Notify about agent failures or issues" },
                            { label: "Weekly reports", description: "Receive weekly usage summary" },
                        ].map((item, i) => (
                            <div key={i} className="flex items-center justify-between p-4">
                                <div>
                                    <p className="text-white">{item.label}</p>
                                    <p className="text-sm text-[#6B6B6B]">{item.description}</p>
                                </div>
                                <label className="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" className="sr-only peer" defaultChecked={i < 2} />
                                    <div className="w-11 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#00D4AA]"></div>
                                </label>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {activeTab === "webhooks" && (
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-medium text-white">Webhooks</h2>
                        <Button size="sm">
                            <Plus className="w-4 h-4 mr-2" />
                            Add Webhook
                        </Button>
                    </div>

                    <div className="space-y-3">
                        {webhooks.map((webhook) => (
                            <div
                                key={webhook.id}
                                className="bg-[#111111] border border-white/10 rounded-lg p-5"
                            >
                                <div className="flex items-start justify-between mb-3">
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <h3 className="font-medium text-white">{webhook.name}</h3>
                                            <span className={`px-2 py-0.5 text-xs rounded-full ${webhook.active
                                                    ? "bg-[#00D4AA]/10 text-[#00D4AA]"
                                                    : "bg-white/5 text-[#6B6B6B]"
                                                }`}>
                                                {webhook.active ? "Active" : "Inactive"}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <code className="text-xs text-[#B0B0B0] bg-[#0A0A0A] px-2 py-1 rounded">
                                                {webhook.url}
                                            </code>
                                            <button className="text-[#6B6B6B] hover:text-[#00D4AA]">
                                                <Copy className="w-3 h-3" />
                                            </button>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-1">
                                        <button className="p-2 rounded-lg text-[#6B6B6B] hover:text-white hover:bg-white/5">
                                            <Edit2 className="w-4 h-4" />
                                        </button>
                                        <button className="p-2 rounded-lg text-[#6B6B6B] hover:text-[#FF4757] hover:bg-[#FF4757]/10">
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    {webhook.events.map((event) => (
                                        <span
                                            key={event}
                                            className="px-2 py-1 text-xs bg-white/5 text-[#B0B0B0] rounded"
                                        >
                                            {event}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
