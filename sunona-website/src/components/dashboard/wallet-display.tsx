/**
 * Wallet Display Component
 * Shows user's balance with real-time updates and low balance warnings
 */
"use client";

import { useEffect } from "react";
import { useAuthStore, selectWallet, selectBalanceStatus } from "@/lib/store/auth-store";
import { Wallet, AlertTriangle, TrendingDown } from "lucide-react";

interface WalletDisplayProps {
    variant?: "header" | "card" | "minimal";
    showTopUp?: boolean;
}

export function WalletDisplay({ variant = "header", showTopUp = true }: WalletDisplayProps) {
    const wallet = useAuthStore(selectWallet);
    const balanceStatus = useAuthStore(selectBalanceStatus);
    const refreshWallet = useAuthStore((state) => state.refreshWallet);

    // Refresh wallet on mount and every 60 seconds
    useEffect(() => {
        refreshWallet();
        const interval = setInterval(refreshWallet, 60000);
        return () => clearInterval(interval);
    }, [refreshWallet]);

    if (!wallet) {
        return (
            <div className="animate-pulse bg-gray-800 rounded-lg h-10 w-28" />
        );
    }

    const formatBalance = (amount: number) => {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: wallet.currency,
            minimumFractionDigits: 2,
        }).format(amount);
    };

    const statusColors = {
        healthy: "text-green-400 bg-green-500/10",
        low: "text-yellow-400 bg-yellow-500/10",
        critical: "text-red-400 bg-red-500/10",
    };

    if (variant === "minimal") {
        return (
            <div className="flex items-center gap-2">
                <Wallet className="w-4 h-4 text-cyan-400" />
                <span className={`font-mono font-medium ${balanceStatus === "critical" ? "text-red-400" :
                        balanceStatus === "low" ? "text-yellow-400" : "text-white"
                    }`}>
                    {formatBalance(wallet.balance)}
                </span>
            </div>
        );
    }

    if (variant === "card") {
        return (
            <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">Wallet Balance</h3>
                    <div className={`p-2 rounded-lg ${statusColors[balanceStatus]}`}>
                        {balanceStatus === "critical" ? (
                            <AlertTriangle className="w-5 h-5" />
                        ) : balanceStatus === "low" ? (
                            <TrendingDown className="w-5 h-5" />
                        ) : (
                            <Wallet className="w-5 h-5" />
                        )}
                    </div>
                </div>

                <div className="mb-4">
                    <p className="text-3xl font-bold text-white font-mono">
                        {formatBalance(wallet.balance)}
                    </p>
                    <p className={`text-sm mt-1 ${balanceStatus === "critical" ? "text-red-400" :
                            balanceStatus === "low" ? "text-yellow-400" : "text-gray-400"
                        }`}>
                        {balanceStatus === "critical" && "⚠️ Balance critically low!"}
                        {balanceStatus === "low" && "Balance running low"}
                        {balanceStatus === "healthy" && "Available Balance"}
                    </p>
                </div>

                {showTopUp && (
                    <button className="w-full py-2.5 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg transition-colors">
                        Add Funds
                    </button>
                )}

                {wallet.autoPayEnabled && (
                    <p className="text-xs text-gray-500 mt-3 text-center">
                        ✓ Auto-pay enabled
                    </p>
                )}
            </div>
        );
    }

    // Header variant (default)
    return (
        <div className="flex items-center gap-3">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${statusColors[balanceStatus]}`}>
                {balanceStatus === "critical" ? (
                    <AlertTriangle className="w-4 h-4" />
                ) : (
                    <Wallet className="w-4 h-4" />
                )}
                <span className="font-mono font-medium text-sm">
                    {formatBalance(wallet.balance)}
                </span>
            </div>

            {showTopUp && wallet.balance < 100 && (
                <button className="text-xs text-cyan-400 hover:text-cyan-300 font-medium">
                    + Add
                </button>
            )}
        </div>
    );
}
