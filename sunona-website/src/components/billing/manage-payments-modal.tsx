/**
 * Manage Payments Modal Component - Sunona Style
 * Add Funds + Auto Recharge tabs
 */
"use client";

import * as React from "react";
import { X, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ManagePaymentsModalProps {
    isOpen: boolean;
    onClose: () => void;
    currentBalance: number;
}

const pricingTiers = [
    { amount: 10, minutes: 250, label: "Starter" },
    { amount: 50, minutes: 1250, label: "Basic" },
    { amount: 100, minutes: 2500, label: "Growth" },
    { amount: 250, minutes: 6250, label: "Pro", discount: "5% extra" },
    { amount: 500, minutes: 12500, label: "Business", discount: "7% extra" },
    { amount: 1000, minutes: 25000, label: "Enterprise", discount: "10% extra" },
];

export function ManagePaymentsModal({ isOpen, onClose, currentBalance }: ManagePaymentsModalProps) {
    const [activeTab, setActiveTab] = React.useState<"add" | "auto">("add");
    const [pricingType, setPricingType] = React.useState<"payg" | "fixed">("payg");
    const [selectedAmount, setSelectedAmount] = React.useState<number>(10);
    const [autoRechargeAmount, setAutoRechargeAmount] = React.useState("10");
    const [triggerBalance, setTriggerBalance] = React.useState("10");
    const [isProcessing, setIsProcessing] = React.useState(false);

    if (!isOpen) return null;

    const handleAddFunds = async () => {
        setIsProcessing(true);
        await new Promise((r) => setTimeout(r, 1500));
        setIsProcessing(false);
        onClose();
    };

    const handleEnableAutoRecharge = async () => {
        setIsProcessing(true);
        await new Promise((r) => setTimeout(r, 1000));
        setIsProcessing(false);
        onClose();
    };

    return (
        <>
            <div className="fixed inset-0 bg-black/50 z-50" onClick={onClose} />
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-xl bg-white rounded-xl shadow-xl z-50">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-100">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900">Manage payments</h2>
                        <p className="text-sm text-gray-500">Manage automated payments and adding credits to your account</p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200">
                    <button
                        onClick={() => setActiveTab("add")}
                        className={`flex-1 py-3 text-sm font-medium border-b-2 -mb-px transition-colors ${activeTab === "add"
                            ? "border-blue-500 text-blue-600"
                            : "border-transparent text-gray-500 hover:text-gray-700"
                            }`}
                    >
                        Add Funds
                    </button>
                    <button
                        onClick={() => setActiveTab("auto")}
                        className={`flex-1 py-3 text-sm font-medium border-b-2 -mb-px transition-colors ${activeTab === "auto"
                            ? "border-blue-500 text-blue-600"
                            : "border-transparent text-gray-500 hover:text-gray-700"
                            }`}
                    >
                        Auto Recharge
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    {activeTab === "add" ? (
                        <div className="space-y-6">
                            {/* Pricing Type */}
                            <div className="flex gap-4">
                                <label className={`flex-1 p-4 border rounded-lg cursor-pointer transition-colors ${pricingType === "payg" ? "border-blue-500 bg-blue-50" : "border-gray-200"
                                    }`}>
                                    <input
                                        type="radio"
                                        checked={pricingType === "payg"}
                                        onChange={() => setPricingType("payg")}
                                        className="sr-only"
                                    />
                                    <div className="flex items-center gap-3">
                                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${pricingType === "payg" ? "border-blue-500" : "border-gray-300"
                                            }`}>
                                            {pricingType === "payg" && <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />}
                                        </div>
                                        <div>
                                            <p className="font-medium text-gray-900">Pay as you go</p>
                                            <p className="text-xs text-gray-500">Perfect for small businesses.</p>
                                        </div>
                                    </div>
                                </label>

                                <label className={`flex-1 p-4 border rounded-lg cursor-pointer transition-colors relative ${pricingType === "fixed" ? "border-blue-500 bg-blue-50" : "border-gray-200"
                                    }`}>
                                    <span className="absolute -top-2 right-3 px-2 py-0.5 bg-blue-500 text-white text-xs rounded-full">
                                        Recommended
                                    </span>
                                    <input
                                        type="radio"
                                        checked={pricingType === "fixed"}
                                        onChange={() => setPricingType("fixed")}
                                        className="sr-only"
                                    />
                                    <div className="flex items-center gap-3">
                                        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${pricingType === "fixed" ? "border-blue-500" : "border-gray-300"
                                            }`}>
                                            {pricingType === "fixed" && <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />}
                                        </div>
                                        <div>
                                            <p className="font-medium text-gray-900">Fixed pricing</p>
                                            <p className="text-xs text-gray-500">Suitable for businesses with growing volumes.</p>
                                        </div>
                                    </div>
                                </label>
                            </div>

                            {/* Amount Grid */}
                            <div className="grid grid-cols-3 gap-3">
                                {pricingTiers.map((tier) => (
                                    <button
                                        key={tier.amount}
                                        onClick={() => setSelectedAmount(tier.amount)}
                                        className={`relative p-4 border rounded-lg text-left transition-colors ${selectedAmount === tier.amount
                                            ? "border-blue-500 bg-blue-50"
                                            : "border-gray-200 hover:border-gray-300"
                                            }`}
                                    >
                                        {tier.discount && (
                                            <span className="absolute -top-2 right-2 px-1.5 py-0.5 bg-green-100 text-green-700 text-[10px] rounded">
                                                {tier.discount}
                                            </span>
                                        )}
                                        <p className="font-semibold text-gray-900">{tier.label} (${tier.amount})</p>
                                        <p className="text-xs text-gray-500">~{tier.minutes.toLocaleString()} minutes</p>
                                    </button>
                                ))}
                            </div>

                            {/* Add Button */}
                            <Button
                                className="w-full"
                                onClick={handleAddFunds}
                                disabled={isProcessing}
                            >
                                {isProcessing ? "Processing..." : `Add $${selectedAmount} to balance`}
                            </Button>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Recharge Amount */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Recharge Amount ($)
                                </label>
                                <p className="text-xs text-gray-500 mb-2">
                                    Auto-recharge with amount (minimum: $10)
                                </p>
                                <input
                                    type="number"
                                    value={autoRechargeAmount}
                                    onChange={(e) => setAutoRechargeAmount(e.target.value)}
                                    min="10"
                                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                                />
                            </div>

                            {/* Trigger Balance */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">
                                    Trigger When Balance Falls Below ($)
                                </label>
                                <p className="text-xs text-gray-500 mb-2">
                                    Auto-recharge when balance drops below this amount (minimum: $10)
                                </p>
                                <input
                                    type="number"
                                    value={triggerBalance}
                                    onChange={(e) => setTriggerBalance(e.target.value)}
                                    min="10"
                                    className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                                />
                            </div>

                            {/* Summary */}
                            <div className="p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
                                Automatically{" "}
                                <span className="text-blue-600 underline">charge ${autoRechargeAmount}</span>
                                {" "}when your balance drops{" "}
                                <span className="text-blue-600 underline">below ${triggerBalance}</span>.
                            </div>

                            {/* Warning for India */}
                            <div className="p-3 bg-red-50 border border-red-100 rounded-lg text-xs text-red-600">
                                Auto-recharge is currently unavailable for cards issued in India due to RBI regulations.
                            </div>

                            {/* Enable Button */}
                            <Button
                                className="w-full"
                                onClick={handleEnableAutoRecharge}
                                disabled={isProcessing}
                            >
                                {isProcessing ? "Enabling..." : "Enable auto recharge"}
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
