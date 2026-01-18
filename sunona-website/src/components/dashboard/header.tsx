/**
 * Sunona Dashboard Header
 * Sunona-inspired with promo banner, wallet balance, and help
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    Plus,
    Wallet,
    HelpCircle,
    ChevronDown,
    LogOut,
    Settings,
    CreditCard,
    User,
    Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore, selectWallet } from "@/lib/store/auth-store";

export function DashboardHeader() {
    const router = useRouter();
    const { user, logout } = useAuthStore();
    const wallet = useAuthStore(selectWallet);
    const [userMenuOpen, setUserMenuOpen] = React.useState(false);

    const balance = wallet?.balance ?? 0;
    const balanceStatus = balance < 5 ? "critical" : balance < 25 ? "low" : "healthy";

    return (
        <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
            {/* Promo Banner */}
            <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-blue-50 to-purple-50 rounded-full border border-blue-100">
                    <Sparkles className="w-4 h-4 text-blue-500" />
                    <span className="text-xs text-gray-700">
                        <span className="font-medium text-blue-600">Try Sunona Pilots:</span>
                        {" "}Ready Agent + Analytics + Free Phone Number
                    </span>
                    <Link
                        href="/dashboard/agents/new"
                        className="text-xs font-medium text-blue-600 hover:text-blue-700 ml-2"
                    >
                        Book a call →
                    </Link>
                </div>
            </div>

            {/* Right Side */}
            <div className="flex items-center gap-4">
                {/* Wallet Balance */}
                <Link
                    href="/dashboard/billing"
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors ${balanceStatus === "critical"
                            ? "bg-red-50 text-red-700 hover:bg-red-100"
                            : balanceStatus === "low"
                                ? "bg-amber-50 text-amber-700 hover:bg-amber-100"
                                : "bg-gray-50 text-gray-700 hover:bg-gray-100"
                        }`}
                >
                    <Wallet className="w-4 h-4" />
                    <span className="text-sm font-medium">
                        ${balance.toFixed(2)}
                    </span>
                </Link>

                {/* Add Funds Button */}
                <Button
                    size="sm"
                    onClick={() => router.push("/dashboard/billing")}
                    className="h-8 text-xs"
                >
                    <Plus className="w-3.5 h-3.5 mr-1" />
                    Add more funds
                </Button>

                {/* Help */}
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
                    <HelpCircle className="w-5 h-5" />
                </button>

                {/* User Menu */}
                <div className="relative">
                    <button
                        onClick={() => setUserMenuOpen(!userMenuOpen)}
                        className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                            <span className="text-xs font-semibold text-white">
                                {user?.name?.charAt(0)?.toUpperCase() || "U"}
                            </span>
                        </div>
                        <ChevronDown className="w-4 h-4 text-gray-400" />
                    </button>

                    {userMenuOpen && (
                        <>
                            <div
                                className="fixed inset-0 z-40"
                                onClick={() => setUserMenuOpen(false)}
                            />
                            <div className="absolute right-0 top-full mt-1 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50">
                                {/* User Info */}
                                <div className="px-4 py-3 border-b border-gray-100">
                                    <p className="text-sm font-medium text-gray-900">
                                        {user?.name || "User"}
                                    </p>
                                    <p className="text-xs text-gray-500 truncate">
                                        {user?.email || "user@example.com"}
                                    </p>
                                </div>

                                {/* Menu Items */}
                                <div className="py-1">
                                    <Link
                                        href="/dashboard/settings"
                                        className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                                        onClick={() => setUserMenuOpen(false)}
                                    >
                                        <User className="w-4 h-4 text-gray-400" />
                                        Profile
                                    </Link>
                                    <Link
                                        href="/dashboard/billing"
                                        className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                                        onClick={() => setUserMenuOpen(false)}
                                    >
                                        <CreditCard className="w-4 h-4 text-gray-400" />
                                        Billing
                                    </Link>
                                    <Link
                                        href="/dashboard/settings"
                                        className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                                        onClick={() => setUserMenuOpen(false)}
                                    >
                                        <Settings className="w-4 h-4 text-gray-400" />
                                        Settings
                                    </Link>
                                </div>

                                <div className="border-t border-gray-100 pt-1">
                                    <button
                                        onClick={() => {
                                            setUserMenuOpen(false);
                                            logout();
                                        }}
                                        className="flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50 w-full"
                                    >
                                        <LogOut className="w-4 h-4" />
                                        Log out
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </header>
    );
}
