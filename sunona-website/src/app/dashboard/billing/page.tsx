/**
 * Billing Page - Light Theme
 * Manage billing and add funds
 */
"use client";

import * as React from "react";
import {
    CreditCard,
    Plus,
    DollarSign,
    TrendingUp,
    Calendar,
    Download,
    Wallet,
    X,
} from "lucide-react";

const transactionHistory = [
    { id: "tx-1", type: "top-up", amount: 50, date: "2025-01-11", method: "Credit Card", status: "completed" },
    { id: "tx-2", type: "usage", amount: -12.50, date: "2025-01-10", method: "API Calls", status: "completed" },
    { id: "tx-3", type: "usage", amount: -8.25, date: "2025-01-09", method: "API Calls", status: "completed" },
    { id: "tx-4", type: "top-up", amount: 100, date: "2025-01-05", method: "Credit Card", status: "completed" },
];

export default function BillingPage() {
    const [showAddFundsModal, setShowAddFundsModal] = React.useState(false);
    const [amount, setAmount] = React.useState("50");
    const balance = 129.25;

    const predefinedAmounts = [25, 50, 100, 250, 500];

    return (
        <div className="max-w-4xl">
            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">Billing</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Manage your account balance and billing
                    </p>
                </div>
                <button
                    onClick={() => setShowAddFundsModal(true)}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    Add Funds
                </button>
            </div>

            {/* Balance Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500">Current Balance</span>
                        <Wallet className="w-5 h-5 text-blue-600" />
                    </div>
                    <p className="text-3xl font-bold text-gray-900">${balance.toFixed(2)}</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500">This Month Usage</span>
                        <TrendingUp className="w-5 h-5 text-emerald-600" />
                    </div>
                    <p className="text-3xl font-bold text-gray-900">$20.75</p>
                </div>
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-500">Auto-Recharge</span>
                        <CreditCard className="w-5 h-5 text-gray-400" />
                    </div>
                    <p className="text-lg font-medium text-gray-900">Disabled</p>
                    <button className="text-xs text-blue-600 hover:underline mt-1">Enable</button>
                </div>
            </div>

            {/* Transaction History */}
            <div className="bg-white border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
                    <h2 className="font-medium text-gray-900">Transaction History</h2>
                    <button className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900">
                        <Download className="w-4 h-4" />
                        Export
                    </button>
                </div>
                <div className="divide-y divide-gray-100">
                    {transactionHistory.map((tx) => (
                        <div key={tx.id} className="px-4 py-3 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${tx.type === "top-up"
                                    ? "bg-emerald-100 text-emerald-600"
                                    : "bg-gray-100 text-gray-600"
                                    }`}>
                                    {tx.type === "top-up" ? <Plus className="w-4 h-4" /> : <DollarSign className="w-4 h-4" />}
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-gray-900">
                                        {tx.type === "top-up" ? "Added Funds" : "Usage Charges"}
                                    </p>
                                    <p className="text-xs text-gray-500">{tx.method}</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className={`font-medium ${tx.amount > 0 ? "text-emerald-600" : "text-gray-900"}`}>
                                    {tx.amount > 0 ? "+" : ""}${Math.abs(tx.amount).toFixed(2)}
                                </p>
                                <p className="text-xs text-gray-500">{tx.date}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Add Funds Modal */}
            {showAddFundsModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl max-w-md w-full">
                        <div className="flex items-center justify-between p-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Add Funds</h3>
                            <button onClick={() => setShowAddFundsModal(false)} className="text-gray-400 hover:text-gray-600">
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="p-4 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Select Amount</label>
                                <div className="grid grid-cols-5 gap-2">
                                    {predefinedAmounts.map((amt) => (
                                        <button
                                            key={amt}
                                            onClick={() => setAmount(String(amt))}
                                            className={`py-2 text-sm font-medium rounded-lg border transition-colors ${amount === String(amt)
                                                ? "bg-blue-600 text-white border-blue-600"
                                                : "bg-white text-gray-700 border-gray-300 hover:border-blue-300"
                                                }`}
                                        >
                                            ${amt}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Or Enter Custom Amount</label>
                                <div className="relative">
                                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
                                    <input
                                        type="number"
                                        value={amount}
                                        onChange={(e) => setAmount(e.target.value)}
                                        className="w-full pl-7 pr-3 py-2.5 bg-white border border-gray-300 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>
                            </div>
                            <div className="p-3 bg-gray-50 rounded-lg">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-600">Amount</span>
                                    <span className="text-gray-900">${amount}</span>
                                </div>
                                <div className="flex justify-between text-sm mt-2 pt-2 border-t border-gray-200">
                                    <span className="font-medium text-gray-900">Total</span>
                                    <span className="font-medium text-gray-900">${amount}</span>
                                </div>
                            </div>
                        </div>
                        <div className="flex justify-end gap-3 p-4 border-t border-gray-200">
                            <button onClick={() => setShowAddFundsModal(false)} className="px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                                Cancel
                            </button>
                            <button className="px-4 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg">
                                Add ${amount}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
