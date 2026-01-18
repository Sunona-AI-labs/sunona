/**
 * Updated Billing Cost Breakdown Component
 * Works with enhanced multi-key BYOK system
 */
"use client";

import * as React from "react";
import { Calculator, CheckCircle, DollarSign } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    useProviderKeysStore,
    PLATFORM_FEE_PER_MINUTE,
    PLATFORM_PROVIDER_COSTS,
} from "@/lib/store/provider-keys-store";

interface CostBreakdownProps {
    estimatedMinutes?: number;
}

export function BillingCostBreakdown({ estimatedMinutes = 100 }: CostBreakdownProps) {
    const { getBillingMode, getEstimatedCostPerMinute, getTotalKeyCount } = useProviderKeysStore();
    const billingMode = getBillingMode();
    const costPerMinute = getEstimatedCostPerMinute();
    const totalKeys = getTotalKeyCount();

    // Calculate costs
    const platformFee = PLATFORM_FEE_PER_MINUTE * estimatedMinutes;

    const llmCost = billingMode.llm === "platform"
        ? PLATFORM_PROVIDER_COSTS.llm * estimatedMinutes
        : 0;
    const sttCost = billingMode.stt === "platform"
        ? PLATFORM_PROVIDER_COSTS.stt * estimatedMinutes
        : 0;
    const ttsCost = billingMode.tts === "platform"
        ? PLATFORM_PROVIDER_COSTS.tts * estimatedMinutes
        : 0;
    const telephonyCost = billingMode.telephony === "platform"
        ? PLATFORM_PROVIDER_COSTS.telephony * estimatedMinutes
        : 0;

    const totalCost = costPerMinute * estimatedMinutes;
    const providerCosts = llmCost + sttCost + ttsCost + telephonyCost;

    // Calculate max savings
    const maxCostPerMinute = PLATFORM_FEE_PER_MINUTE +
        PLATFORM_PROVIDER_COSTS.llm +
        PLATFORM_PROVIDER_COSTS.stt +
        PLATFORM_PROVIDER_COSTS.tts +
        PLATFORM_PROVIDER_COSTS.telephony;
    const potentialSavings = (maxCostPerMinute - costPerMinute) * estimatedMinutes;

    // Count BYOK services
    const byokCount = [
        billingMode.llm === "byok",
        billingMode.stt === "byok",
        billingMode.tts === "byok",
        billingMode.telephony === "byok",
    ].filter(Boolean).length;

    return (
        <Card className="bg-white border border-gray-200">
            <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Calculator className="w-5 h-5 text-blue-600" />
                        <CardTitle className="text-base">Cost Estimate</CardTitle>
                    </div>
                    <div className="flex items-center gap-2">
                        <Badge variant="default">
                            {estimatedMinutes} min
                        </Badge>
                        {byokCount > 0 && (
                            <Badge variant="success" size="sm">
                                {byokCount}/4 BYOK
                            </Badge>
                        )}
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {/* Rate per minute */}
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                        <span className="text-sm text-gray-600">Your rate</span>
                        <span className="text-lg font-bold text-gray-900">
                            ${costPerMinute.toFixed(3)}/min
                        </span>
                    </div>

                    {/* Breakdown */}
                    <div className="space-y-2">
                        {/* Platform fee - always */}
                        <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                                <CheckCircle className="w-4 h-4 text-green-500" />
                                <span className="text-gray-700">Platform Fee</span>
                            </div>
                            <span className="font-mono text-gray-900">${platformFee.toFixed(2)}</span>
                        </div>

                        {/* LLM */}
                        <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                                {billingMode.llm === "byok" ? (
                                    <CheckCircle className="w-4 h-4 text-green-500" />
                                ) : (
                                    <div className="w-4 h-4 rounded-full bg-blue-100" />
                                )}
                                <span className={billingMode.llm === "byok" ? "text-green-700" : "text-gray-700"}>
                                    LLM {billingMode.llm === "byok" ? "(Your Keys)" : "(Platform)"}
                                </span>
                            </div>
                            <span className={`font-mono ${billingMode.llm === "byok" ? "text-green-600" : "text-gray-900"}`}>
                                {billingMode.llm === "byok" ? "$0.00" : `$${llmCost.toFixed(2)}`}
                            </span>
                        </div>

                        {/* STT */}
                        <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                                {billingMode.stt === "byok" ? (
                                    <CheckCircle className="w-4 h-4 text-green-500" />
                                ) : (
                                    <div className="w-4 h-4 rounded-full bg-purple-100" />
                                )}
                                <span className={billingMode.stt === "byok" ? "text-green-700" : "text-gray-700"}>
                                    STT {billingMode.stt === "byok" ? "(Your Keys)" : "(Platform)"}
                                </span>
                            </div>
                            <span className={`font-mono ${billingMode.stt === "byok" ? "text-green-600" : "text-gray-900"}`}>
                                {billingMode.stt === "byok" ? "$0.00" : `$${sttCost.toFixed(2)}`}
                            </span>
                        </div>

                        {/* TTS */}
                        <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                                {billingMode.tts === "byok" ? (
                                    <CheckCircle className="w-4 h-4 text-green-500" />
                                ) : (
                                    <div className="w-4 h-4 rounded-full bg-amber-100" />
                                )}
                                <span className={billingMode.tts === "byok" ? "text-green-700" : "text-gray-700"}>
                                    TTS {billingMode.tts === "byok" ? "(Your Keys)" : "(Platform)"}
                                </span>
                            </div>
                            <span className={`font-mono ${billingMode.tts === "byok" ? "text-green-600" : "text-gray-900"}`}>
                                {billingMode.tts === "byok" ? "$0.00" : `$${ttsCost.toFixed(2)}`}
                            </span>
                        </div>

                        {/* Telephony */}
                        <div className="flex items-center justify-between text-sm">
                            <div className="flex items-center gap-2">
                                {billingMode.telephony === "byok" ? (
                                    <CheckCircle className="w-4 h-4 text-green-500" />
                                ) : (
                                    <div className="w-4 h-4 rounded-full bg-green-100" />
                                )}
                                <span className={billingMode.telephony === "byok" ? "text-green-700" : "text-gray-700"}>
                                    Telephony {billingMode.telephony === "byok" ? "(Your Keys)" : "(Platform)"}
                                </span>
                            </div>
                            <span className={`font-mono ${billingMode.telephony === "byok" ? "text-green-600" : "text-gray-900"}`}>
                                {billingMode.telephony === "byok" ? "$0.00" : `$${telephonyCost.toFixed(2)}`}
                            </span>
                        </div>
                    </div>

                    {/* Total */}
                    <div className="flex items-center justify-between pt-3 border-t border-gray-200">
                        <span className="font-semibold text-gray-900">Estimated Total</span>
                        <span className="text-xl font-bold text-gray-900">
                            ${totalCost.toFixed(2)}
                        </span>
                    </div>

                    {/* Savings */}
                    {potentialSavings > 0 && (
                        <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-green-800">
                                    💰 Saving with {totalKeys} BYOK key{totalKeys !== 1 ? "s" : ""}
                                </span>
                                <span className="font-bold text-green-700">
                                    ${potentialSavings.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Tip */}
                    {byokCount < 4 && (
                        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <p className="text-xs text-blue-800">
                                💡 Add your own {4 - byokCount} more API key{4 - byokCount !== 1 ? "s" : ""} to
                                pay only ${(PLATFORM_FEE_PER_MINUTE * estimatedMinutes).toFixed(2)} for
                                {estimatedMinutes} minutes!
                            </p>
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}

/**
 * Mini billing indicator
 */
export function BillingModeIndicator() {
    const { getBillingMode, getTotalKeyCount } = useProviderKeysStore();
    const billingMode = getBillingMode();
    const totalKeys = getTotalKeyCount();

    const byokCount = [
        billingMode.llm === "byok",
        billingMode.stt === "byok",
        billingMode.tts === "byok",
        billingMode.telephony === "byok",
    ].filter(Boolean).length;

    return (
        <div className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 rounded-md">
            <DollarSign className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-xs font-medium text-gray-700">
                {totalKeys > 0 ? (
                    <span className="text-green-600">{byokCount}/4 BYOK</span>
                ) : (
                    "Platform"
                )}
            </span>
        </div>
    );
}
