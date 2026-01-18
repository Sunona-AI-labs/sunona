/**
 * Phone Numbers Page - Light Theme
 * Manage phone numbers for inbound and outbound calls
 */
"use client";

import * as React from "react";
import {
    Phone,
    Plus,
    Search,
    Settings2,
    Trash2,
    Copy,
    ExternalLink,
    PhoneIncoming,
    PhoneOutgoing,
    Globe,
    Check,
    X,
} from "lucide-react";

// Mock phone numbers data
const mockNumbers = [
    {
        id: "num-1",
        number: "+1 (555) 234-5678",
        countryCode: "US",
        type: "local",
        capabilities: ["voice", "sms"],
        status: "active",
        agentAssigned: "Customer Support",
        monthlyRent: 1.50,
        perMinute: 0.02,
    },
    {
        id: "num-2",
        number: "+91 98765 43210",
        countryCode: "IN",
        type: "mobile",
        capabilities: ["voice"],
        status: "active",
        agentAssigned: null,
        monthlyRent: 2.00,
        perMinute: 0.03,
    },
];

export default function PhoneNumbersPage() {
    const [numbers] = React.useState(mockNumbers);
    const [search, setSearch] = React.useState("");
    const [showPurchaseModal, setShowPurchaseModal] = React.useState(false);

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <div className="max-w-full">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">My Numbers</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Manage your phone numbers for inbound and outbound calls
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                        <Settings2 className="w-4 h-4" />
                        Connect Provider
                    </button>
                    <button
                        onClick={() => setShowPurchaseModal(true)}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        <Plus className="w-4 h-4" />
                        Buy phone number
                    </button>
                </div>
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
                    placeholder="Search phone numbers..."
                    style={{ paddingLeft: '40px' }}
                    className="w-full pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-900 placeholder:text-gray-400 hover:border-gray-300 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white transition-all duration-200"
                />
            </div>




            {/* Numbers Table */}
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <table className="w-full">
                    <thead>
                        <tr className="bg-gray-50 border-b border-gray-200">
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Phone Number</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Type</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Capabilities</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Agent Assigned</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Cost</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Status</th>
                            <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider px-4 py-3">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {numbers.map((num) => (
                            <tr key={num.id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <Phone className="w-4 h-4 text-blue-600" />
                                        <span className="font-medium text-gray-900">{num.number}</span>
                                        <button onClick={() => copyToClipboard(num.number)} className="text-gray-400 hover:text-gray-600">
                                            <Copy className="w-3.5 h-3.5" />
                                        </button>
                                    </div>
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-1.5">
                                        <Globe className="w-3.5 h-3.5 text-gray-400" />
                                        <span className="text-sm text-gray-600 capitalize">{num.type}</span>
                                    </div>
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex gap-1">
                                        {num.capabilities.includes("voice") && (
                                            <span className="px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded">Voice</span>
                                        )}
                                        {num.capabilities.includes("sms") && (
                                            <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-700 rounded">SMS</span>
                                        )}
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-600">
                                    {num.agentAssigned || <span className="text-gray-400">Not assigned</span>}
                                </td>
                                <td className="px-4 py-3">
                                    <div className="text-sm">
                                        <div className="text-gray-900">${num.monthlyRent.toFixed(2)}/mo</div>
                                        <div className="text-xs text-gray-500">${num.perMinute.toFixed(2)}/min</div>
                                    </div>
                                </td>
                                <td className="px-4 py-3">
                                    <span className="px-2 py-1 text-xs font-medium rounded-full bg-emerald-100 text-emerald-700">
                                        {num.status}
                                    </span>
                                </td>
                                <td className="px-4 py-3">
                                    <div className="flex items-center gap-2">
                                        <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded">
                                            <Settings2 className="w-4 h-4" />
                                        </button>
                                        <button className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded">
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {numbers.length === 0 && (
                    <div className="text-center py-16">
                        <Phone className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p className="text-sm text-gray-600">No phone numbers yet</p>
                        <p className="text-xs text-gray-400 mt-1">Purchase a number to get started</p>
                    </div>
                )}
            </div>

            {/* Purchase Modal */}
            {showPurchaseModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl max-w-md w-full">
                        <div className="flex items-center justify-between p-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Buy phone number</h3>
                            <button onClick={() => setShowPurchaseModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Country</label>
                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                    <option>United States (+1)</option>
                                    <option>India (+91)</option>
                                    <option>United Kingdom (+44)</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Number Type</label>
                                <select className="w-full px-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500">
                                    <option>Local</option>
                                    <option>Toll-Free</option>
                                    <option>Mobile</option>
                                </select>
                            </div>
                        </div>
                        <div className="flex justify-end gap-3 p-4 border-t border-gray-200">
                            <button onClick={() => setShowPurchaseModal(false)} className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                                Cancel
                            </button>
                            <button className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg">
                                Search Numbers
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
