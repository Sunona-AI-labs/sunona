/**
 * Post-Call Cost Summary Component
 * Shows detailed cost breakdown after a call ends
 */
"use client";

import * as React from "react";
import { CheckCircle, Clock, Phone, TrendingDown, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface PostCallCostProps {
    callId: string;
    agentName: string;
    durationSeconds: number;
    costBreakdown: {
        platform_fee: number;
        llm_cost: number;
        stt_cost: number;
        tts_cost: number;
        telephony_cost: number;
        total: number;
        byok_services: string[];
    };
    newBalance: number;
    onClose: () => void;
}

export function PostCallCostSummary({
    callId,
    agentName,
    durationSeconds,
    costBreakdown,
    newBalance,
    onClose,
}: PostCallCostProps) {
    const formatDuration = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    const byokServices = costBreakdown.byok_services || [];
    const savedAmount = byokServices.length * 0.02 * (durationSeconds / 60);

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <Card className="w-full max-w-md mx-4 bg-white">
                <CardContent className="p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                                <CheckCircle className="w-5 h-5 text-green-600" />
                            </div>
                            <div>
                                <h3 className="font-semibold text-gray-900">Call Completed</h3>
                                <p className="text-sm text-gray-500">{agentName}</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-1 hover:bg-gray-100 rounded"
                        >
                            <X className="w-5 h-5 text-gray-400" />
                        </button>
                    </div>

                    {/* Duration */}
                    <div className="flex items-center justify-center gap-2 py-4 bg-gray-50 rounded-lg mb-4">
                        <Clock className="w-5 h-5 text-gray-500" />
                        <span className="text-2xl font-bold text-gray-900">
                            {formatDuration(durationSeconds)}
                        </span>
                    </div>

                    {/* Cost Breakdown */}
                    <div className="space-y-2 mb-4">
                        <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Platform Fee</span>
                            <span className="font-mono">${costBreakdown.platform_fee.toFixed(4)}</span>
                        </div>

                        <div className="flex justify-between text-sm">
                            <span className={byokServices.includes("llm") ? "text-green-600" : "text-gray-600"}>
                                LLM {byokServices.includes("llm") && "(BYOK)"}
                            </span>
                            <span className={`font-mono ${byokServices.includes("llm") ? "text-green-600" : ""}`}>
                                ${costBreakdown.llm_cost.toFixed(4)}
                            </span>
                        </div>

                        <div className="flex justify-between text-sm">
                            <span className={byokServices.includes("stt") ? "text-green-600" : "text-gray-600"}>
                                STT {byokServices.includes("stt") && "(BYOK)"}
                            </span>
                            <span className={`font-mono ${byokServices.includes("stt") ? "text-green-600" : ""}`}>
                                ${costBreakdown.stt_cost.toFixed(4)}
                            </span>
                        </div>

                        <div className="flex justify-between text-sm">
                            <span className={byokServices.includes("tts") ? "text-green-600" : "text-gray-600"}>
                                TTS {byokServices.includes("tts") && "(BYOK)"}
                            </span>
                            <span className={`font-mono ${byokServices.includes("tts") ? "text-green-600" : ""}`}>
                                ${costBreakdown.tts_cost.toFixed(4)}
                            </span>
                        </div>

                        <div className="flex justify-between text-sm">
                            <span className={byokServices.includes("telephony") ? "text-green-600" : "text-gray-600"}>
                                Telephony {byokServices.includes("telephony") && "(BYOK)"}
                            </span>
                            <span className={`font-mono ${byokServices.includes("telephony") ? "text-green-600" : ""}`}>
                                ${costBreakdown.telephony_cost.toFixed(4)}
                            </span>
                        </div>
                    </div>

                    {/* Total */}
                    <div className="flex justify-between py-3 border-t border-gray-200">
                        <span className="font-semibold text-gray-900">Total Charged</span>
                        <span className="text-lg font-bold text-gray-900">
                            ${costBreakdown.total.toFixed(4)}
                        </span>
                    </div>

                    {/* Savings */}
                    {byokServices.length > 0 && (
                        <div className="p-3 bg-green-50 border border-green-200 rounded-lg mb-4">
                            <div className="flex items-center gap-2">
                                <TrendingDown className="w-4 h-4 text-green-600" />
                                <span className="text-sm text-green-800">
                                    Saved ~${savedAmount.toFixed(2)} with {byokServices.length} BYOK service{byokServices.length > 1 ? "s" : ""}!
                                </span>
                            </div>
                        </div>
                    )}

                    {/* New Balance */}
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg mb-4">
                        <div className="flex justify-between">
                            <span className="text-sm text-blue-800">New Wallet Balance</span>
                            <span className="font-bold text-blue-900">${newBalance.toFixed(2)}</span>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3">
                        <Button variant="ghost" className="flex-1" onClick={onClose}>
                            Close
                        </Button>
                        <Button className="flex-1">
                            View Details
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

/**
 * Live Cost Display During Call
 */
interface LiveCostProps {
    currentCost: number;
    durationSeconds: number;
    isActive: boolean;
}

export function LiveCostDisplay({ currentCost, durationSeconds, isActive }: LiveCostProps) {
    const formatDuration = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    if (!isActive) return null;

    return (
        <div className="fixed bottom-4 right-4 z-50">
            <Card className="bg-gray-900 border-gray-700 shadow-xl">
                <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                            <span className="text-sm text-gray-400">Live</span>
                        </div>
                        <div className="text-center">
                            <p className="text-2xl font-mono font-bold text-white">
                                {formatDuration(durationSeconds)}
                            </p>
                            <p className="text-xs text-gray-500">Duration</p>
                        </div>
                        <div className="text-center border-l border-gray-700 pl-4">
                            <p className="text-xl font-mono font-bold text-green-400">
                                ${currentCost.toFixed(4)}
                            </p>
                            <p className="text-xs text-gray-500">Cost</p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
