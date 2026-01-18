/**
 * Subaccounts Settings Page - Sunona Style
 * Manage sub accounts and their usage
 */
"use client";

import * as React from "react";
import {
    Plus,
    Users,
    BarChart3,
    Trash2,
    Edit,
    Copy,
    CheckCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// Tab definitions
const tabs = [
    { id: "accounts", label: "Sub Accounts" },
    { id: "usage", label: "Usage Details" },
];

interface SubAccount {
    id: string;
    name: string;
    email: string;
    apiKey: string;
    status: "active" | "suspended";
    totalSpend: number;
    callCount: number;
    createdAt: string;
}

export default function SubaccountsPage() {
    const [activeTab, setActiveTab] = React.useState("accounts");
    const [subAccounts, setSubAccounts] = React.useState<SubAccount[]>([]);
    const [showCreateModal, setShowCreateModal] = React.useState(false);

    return (
        <div className="max-w-5xl">
            {/* Page Header */}
            <div className="mb-6">
                <h1 className="text-xl font-semibold text-gray-900">Subaccounts settings</h1>
                <p className="text-sm text-gray-500 mt-1">
                    Manage sub accounts and their usage
                </p>
            </div>

            {/* Tabs */}
            <div className="flex items-center justify-between border-b border-gray-200 mb-6">
                <div className="flex gap-1">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors ${activeTab === tab.id
                                ? "border-blue-500 text-blue-600"
                                : "border-transparent text-gray-500 hover:text-gray-700"
                                }`}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>
                <Button onClick={() => setShowCreateModal(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Add Sub Account
                </Button>
            </div>

            {/* Tab Content */}
            {activeTab === "accounts" && (
                <SubAccountsTab accounts={subAccounts} />
            )}
            {activeTab === "usage" && (
                <UsageDetailsTab accounts={subAccounts} />
            )}

            {/* Create Modal */}
            {showCreateModal && (
                <CreateSubAccountModal onClose={() => setShowCreateModal(false)} />
            )}
        </div>
    );
}

function SubAccountsTab({ accounts }: { accounts: SubAccount[] }) {
    const [copiedId, setCopiedId] = React.useState<string | null>(null);

    const copyApiKey = (id: string, key: string) => {
        navigator.clipboard.writeText(key);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    if (accounts.length === 0) {
        return (
            <Card>
                <CardContent className="py-12 text-center">
                    <Users className="w-12 h-12 mx-auto mb-4 text-gray-200" />
                    <p className="text-gray-500 mb-4">
                        This is a paid feature. Please{" "}
                        <a href="#" className="text-blue-600 hover:underline">schedule a call</a>
                        {" "}with our team or email us at{" "}
                        <a href="mailto:enterprise@sunona.ai" className="text-blue-600 hover:underline">
                            enterprise@sunona.ai
                        </a>
                    </p>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full">
                <thead className="bg-gray-50">
                    <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Account Name</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Email</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">API Key</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Status</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Total Spend</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Actions</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {accounts.map((account) => (
                        <tr key={account.id}>
                            <td className="px-4 py-3 text-sm text-gray-900">{account.name}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">{account.email}</td>
                            <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <span className="font-mono text-xs text-gray-500">
                                        {account.apiKey.slice(0, 12)}...
                                    </span>
                                    <button
                                        onClick={() => copyApiKey(account.id, account.apiKey)}
                                        className="text-gray-400 hover:text-gray-600"
                                    >
                                        {copiedId === account.id ? (
                                            <CheckCircle className="w-4 h-4 text-green-500" />
                                        ) : (
                                            <Copy className="w-4 h-4" />
                                        )}
                                    </button>
                                </div>
                            </td>
                            <td className="px-4 py-3">
                                <Badge
                                    variant={account.status === "active" ? "success" : "error"}
                                    size="sm"
                                >
                                    {account.status}
                                </Badge>
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">${account.totalSpend.toFixed(2)}</td>
                            <td className="px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <button className="text-gray-400 hover:text-gray-600">
                                        <Edit className="w-4 h-4" />
                                    </button>
                                    <button className="text-gray-400 hover:text-red-500">
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

function UsageDetailsTab({ accounts }: { accounts: SubAccount[] }) {
    if (accounts.length === 0) {
        return (
            <Card>
                <CardContent className="py-12 text-center">
                    <BarChart3 className="w-12 h-12 mx-auto mb-4 text-gray-200" />
                    <p className="text-gray-500">No usage data available.</p>
                    <p className="text-xs text-gray-400 mt-1">
                        Create sub accounts to track their usage
                    </p>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-4 gap-4">
                <Card>
                    <CardContent className="p-4">
                        <p className="text-xs text-gray-500 mb-1">Total Sub Accounts</p>
                        <p className="text-2xl font-bold text-gray-900">{accounts.length}</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <p className="text-xs text-gray-500 mb-1">Total Spend (All)</p>
                        <p className="text-2xl font-bold text-gray-900">
                            ${accounts.reduce((sum, a) => sum + a.totalSpend, 0).toFixed(2)}
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <p className="text-xs text-gray-500 mb-1">Total Calls (All)</p>
                        <p className="text-2xl font-bold text-gray-900">
                            {accounts.reduce((sum, a) => sum + a.callCount, 0)}
                        </p>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="p-4">
                        <p className="text-xs text-gray-500 mb-1">Active Accounts</p>
                        <p className="text-2xl font-bold text-gray-900">
                            {accounts.filter((a) => a.status === "active").length}
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Usage Table */}
            <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Account</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Call Count</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Total Duration</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Total Spend</th>
                            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">Avg Cost/Call</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {accounts.map((account) => (
                            <tr key={account.id}>
                                <td className="px-4 py-3 text-sm text-gray-900">{account.name}</td>
                                <td className="px-4 py-3 text-sm text-gray-600">{account.callCount}</td>
                                <td className="px-4 py-3 text-sm text-gray-600">-</td>
                                <td className="px-4 py-3 text-sm text-gray-900">${account.totalSpend.toFixed(2)}</td>
                                <td className="px-4 py-3 text-sm text-gray-600">
                                    ${account.callCount > 0 ? (account.totalSpend / account.callCount).toFixed(3) : "0.000"}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function CreateSubAccountModal({ onClose }: { onClose: () => void }) {
    const [name, setName] = React.useState("");
    const [email, setEmail] = React.useState("");

    return (
        <>
            <div className="fixed inset-0 bg-black/50 z-50" onClick={onClose} />
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white rounded-xl shadow-xl z-50 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Create Sub Account</h2>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Account Name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g. 'Sales Team'"
                            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="team@company.com"
                            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                        />
                    </div>
                </div>

                <div className="flex justify-end gap-3 mt-6">
                    <Button variant="ghost" onClick={onClose}>Cancel</Button>
                    <Button disabled={!name || !email}>Create Account</Button>
                </div>
            </div>
        </>
    );
}
