/**
 * Sunona Dashboard Sidebar
 * Sunona-inspired clean design with light theme
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    Bot,
    Phone,
    PhoneCall,
    Database,
    Layers,
    Mic2,
    Code2,
    Link2,
    GitBranch,
    Megaphone,
    ChevronDown,
    LogOut,
    Settings,
    Users,
    CreditCard,
    Building2,
    HelpCircle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/lib/store/auth-store";

interface NavItem {
    label: string;
    href: string;
    icon: React.ComponentType<{ className?: string }>;
    badge?: string;
}

const platformNavItems: NavItem[] = [
    { label: "Agent Setup", href: "/dashboard/agents", icon: Bot },
    { label: "Call History", href: "/dashboard/calls", icon: PhoneCall },
    { label: "My Numbers", href: "/dashboard/phone-numbers", icon: Phone },
    { label: "Knowledge Base", href: "/dashboard/knowledge", icon: Database },
    { label: "Batches", href: "/dashboard/batches", icon: Layers },
    { label: "Voice Lab", href: "/dashboard/voice-lab", icon: Mic2 },
    { label: "Developers", href: "/dashboard/developers", icon: Code2 },
    { label: "Providers", href: "/dashboard/providers", icon: Link2 },
    { label: "Workflows", href: "/dashboard/workflows", icon: GitBranch },
    { label: "Campaigns", href: "/dashboard/campaigns", icon: Megaphone },
];

const workplaceItems = [
    { label: "Account Info", href: "/dashboard/settings" },
    { label: "Team Members", href: "/dashboard/team" },
    { label: "Billing & Usage", href: "/dashboard/billing" },
    { label: "API Keys", href: "/dashboard/settings/api-keys" },
];

export function DashboardSidebar() {
    const pathname = usePathname();
    const { user, logout } = useAuthStore();
    const [workplaceOpen, setWorkplaceOpen] = React.useState(false);

    const isActive = (href: string) => {
        if (href === "/dashboard") return pathname === "/dashboard";
        return pathname.startsWith(href);
    };

    return (
        <aside className="fixed inset-y-0 left-0 z-50 w-60 bg-white border-r border-gray-200 flex flex-col">
            {/* Logo */}
            <div className="h-14 flex items-center px-5 border-b border-gray-100">
                <Link href="/dashboard" className="flex items-center gap-2.5">
                    {/* Audio wave icon */}
                    <div className="flex items-center gap-0.5">
                        <div className="w-1 h-3 bg-blue-500 rounded-full" />
                        <div className="w-1 h-5 bg-blue-400 rounded-full" />
                        <div className="w-1 h-7 bg-blue-500 rounded-full" />
                        <div className="w-1 h-5 bg-blue-400 rounded-full" />
                        <div className="w-1 h-3 bg-blue-500 rounded-full" />
                    </div>
                    <span className="text-lg font-bold text-gray-900 tracking-tight">
                        SUNONA
                    </span>
                </Link>
            </div>

            {/* User Profile */}
            <div className="px-4 py-3 border-b border-gray-100">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                        <span className="text-xs font-semibold text-white">
                            {user?.name?.charAt(0)?.toUpperCase() || "U"}
                        </span>
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                            {user?.name || "User"}
                        </p>
                        <p className="text-xs text-green-500 flex items-center gap-1">
                            <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                            Active
                        </p>
                    </div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 overflow-y-auto py-3 px-3">
                {/* Platform Section */}
                <div className="mb-4">
                    <p className="px-3 mb-2 text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
                        Platform
                    </p>
                    <ul className="space-y-0.5">
                        {platformNavItems.map((item) => {
                            const active = isActive(item.href);
                            return (
                                <li key={item.href}>
                                    <Link
                                        href={item.href}
                                        className={cn(
                                            "flex items-center gap-3 px-3 py-2 text-[13px] rounded-lg transition-all",
                                            active
                                                ? "bg-blue-50 text-blue-600 font-medium"
                                                : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                                        )}
                                    >
                                        <item.icon className={cn(
                                            "h-4 w-4 flex-shrink-0",
                                            active ? "text-blue-600" : "text-gray-400"
                                        )} />
                                        <span>{item.label}</span>
                                        {item.badge && (
                                            <span className="ml-auto text-[10px] bg-blue-100 text-blue-600 px-1.5 py-0.5 rounded">
                                                {item.badge}
                                            </span>
                                        )}
                                    </Link>
                                </li>
                            );
                        })}
                    </ul>
                </div>

                {/* Team Section */}
                <div>
                    <p className="px-3 mb-2 text-[10px] font-semibold text-gray-400 uppercase tracking-wider">
                        Team
                    </p>
                    <ul className="space-y-0.5">
                        <li>
                            <button
                                onClick={() => setWorkplaceOpen(!workplaceOpen)}
                                className="w-full flex items-center gap-3 px-3 py-2 text-[13px] rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-all"
                            >
                                <Building2 className="h-4 w-4 flex-shrink-0 text-gray-400" />
                                <span className="flex-1 text-left">Workplace</span>
                                <ChevronDown className={cn(
                                    "h-3.5 w-3.5 text-gray-400 transition-transform",
                                    workplaceOpen && "rotate-180"
                                )} />
                            </button>
                            {workplaceOpen && (
                                <ul className="mt-1 ml-7 space-y-0.5 border-l border-gray-100 pl-3">
                                    {workplaceItems.map((item) => (
                                        <li key={item.href}>
                                            <Link
                                                href={item.href}
                                                className={cn(
                                                    "block py-1.5 text-[13px] transition-colors",
                                                    isActive(item.href)
                                                        ? "text-blue-600 font-medium"
                                                        : "text-gray-500 hover:text-gray-900"
                                                )}
                                            >
                                                {item.label}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </li>
                    </ul>
                </div>
            </nav>

            {/* Help Link */}
            <div className="px-3 py-2 border-t border-gray-100">
                <Link
                    href="/docs"
                    className="flex items-center gap-3 px-3 py-2 text-[13px] text-gray-500 hover:text-gray-900 rounded-lg hover:bg-gray-50 transition-all"
                >
                    <HelpCircle className="h-4 w-4" />
                    <span>Documentation</span>
                </Link>
            </div>

            {/* User Menu */}
            <div className="p-3 border-t border-gray-100">
                <div className="flex items-center gap-3 px-2">
                    <div className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center">
                        <span className="text-xs font-medium text-gray-600">
                            {user?.email?.charAt(0)?.toUpperCase() || "U"}
                        </span>
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-xs text-gray-900 truncate">
                            {user?.email || "user@example.com"}
                        </p>
                    </div>
                    <button
                        onClick={logout}
                        className="p-1.5 text-gray-400 hover:text-red-500 transition-colors rounded hover:bg-red-50"
                        title="Log out"
                    >
                        <LogOut className="h-4 w-4" />
                    </button>
                </div>
            </div>
        </aside>
    );
}
