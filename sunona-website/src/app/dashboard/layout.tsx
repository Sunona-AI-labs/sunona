/**
 * Dashboard Layout - Wraps all dashboard pages
 * Uses shared DashboardShell for consistent UI
 */
"use client";

import * as React from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store/auth-store";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const router = useRouter();
    const { isAuthenticated, isLoading } = useAuthStore();

    React.useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push("/login");
        }
    }, [isAuthenticated, isLoading, router]);

    if (isLoading) {
        return (
            <div className="min-h-screen bg-[#f8fafc] flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 animate-pulse" />
                    <p className="text-gray-600 text-sm animate-pulse">Loading dashboard...</p>
                </div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return null;
    }

    return <DashboardShell>{children}</DashboardShell>;
}
