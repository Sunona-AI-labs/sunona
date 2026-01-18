/**
 * Advanced Dashboard Header - 21st.dev Style
 * Modern header with glassmorphism, balance display, and notifications
 */
"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import * as Tooltip from "@radix-ui/react-tooltip";
import { cn } from "@/lib/utils";
import {
    Search,
    Bell,
    Settings,
    HelpCircle,
    Plus,
    Wallet,
    ChevronDown,
    Sparkles,
} from "lucide-react";

const routeTitles: Record<string, { title: string; subtitle: string }> = {
    "/dashboard": { title: "Dashboard", subtitle: "Overview of your Voice AI platform" },
    "/dashboard/agents": { title: "Agent Setup", subtitle: "Configure and manage your AI agents" },
    "/dashboard/calls": { title: "Call History", subtitle: "View all agent conversations" },
    "/dashboard/phone-numbers": { title: "Phone Numbers", subtitle: "Manage your telephony numbers" },
    "/dashboard/knowledge": { title: "Knowledge Base", subtitle: "Upload and manage RAG documents" },
    "/dashboard/batches": { title: "Batch Calling", subtitle: "Run bulk calling campaigns" },
    "/dashboard/voice-lab": { title: "Voice Lab", subtitle: "Explore and customize voices" },
    "/dashboard/developers": { title: "Developers", subtitle: "API keys and integrations" },
    "/dashboard/providers": { title: "Providers", subtitle: "Connect external AI providers" },
    "/dashboard/workflows": { title: "Workflows", subtitle: "Automate call workflows" },
    "/dashboard/campaigns": { title: "Campaigns", subtitle: "Manage marketing campaigns" },
    "/dashboard/analytics": { title: "Analytics", subtitle: "Insights and performance metrics" },
    "/dashboard/recordings": { title: "Recordings", subtitle: "Access call recordings" },
    "/dashboard/billing": { title: "Billing", subtitle: "Manage payments and invoices" },
    "/dashboard/settings": { title: "Settings", subtitle: "Account preferences" },
    "/dashboard/team": { title: "Team", subtitle: "Manage team members" },
};

export function AdvancedHeader() {
    const pathname = usePathname();
    const pageInfo = routeTitles[pathname] || { title: "Dashboard", subtitle: "Welcome back" };
    const [searchOpen, setSearchOpen] = React.useState(false);

    return (
        <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-gray-100">
            {/* Trial Banner */}
            <div className="bg-gradient-to-r from-amber-500/10 via-orange-500/10 to-red-500/10 border-b border-amber-200/50">
                <div className="max-w-7xl mx-auto px-6 py-2 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm">
                        <Sparkles className="w-4 h-4 text-amber-500" />
                        <span className="text-gray-600">
                            You're on a <span className="font-semibold text-amber-600">trial plan</span>, which limits outbound calls.
                        </span>
                        <a href="/dashboard/billing" className="text-blue-500 hover:text-blue-600 font-medium underline underline-offset-2">
                            Upgrade now
                        </a>
                    </div>
                    <a href="/dashboard/phone-numbers" className="text-sm text-blue-500 hover:text-blue-600 font-medium">
                        Get verified phone numbers →
                    </a>
                </div>
            </div>

            {/* Main Header */}
            <div className="max-w-7xl mx-auto px-6">
                <div className="h-16 flex items-center justify-between gap-4">
                    {/* Left: Page Title */}
                    <div className="flex-1 min-w-0">
                        <h1 className="text-xl font-bold text-gray-900 truncate">
                            {pageInfo.title}
                        </h1>
                        <p className="text-sm text-gray-500 truncate">
                            {pageInfo.subtitle}
                        </p>
                    </div>

                    {/* Center: Search */}
                    <div className="hidden md:flex items-center">
                        <div className={cn(
                            "relative flex items-center transition-all duration-300",
                            searchOpen ? "w-80" : "w-64"
                        )}>
                            <Search className="absolute left-3 w-4 h-4 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search agents, calls, documents..."
                                onFocus={() => setSearchOpen(true)}
                                onBlur={() => setSearchOpen(false)}
                                className={cn(
                                    "w-full pl-9 pr-4 py-2 text-sm",
                                    "bg-gray-50 border border-gray-200 rounded-xl",
                                    "text-gray-900 placeholder:text-gray-400",
                                    "focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500",
                                    "transition-all duration-200"
                                )}
                            />
                            <kbd className="absolute right-3 px-1.5 py-0.5 text-[10px] font-medium text-gray-400 bg-gray-100 rounded border border-gray-200">
                                ⌘K
                            </kbd>
                        </div>
                    </div>

                    {/* Right: Actions */}
                    <div className="flex items-center gap-2">
                        {/* Balance */}
                        <Tooltip.Provider>
                            <Tooltip.Root>
                                <Tooltip.Trigger asChild>
                                    <button className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-lg text-sm font-medium text-emerald-700 hover:bg-emerald-100 transition-colors">
                                        <Wallet className="w-4 h-4" />
                                        <span>$5.00</span>
                                    </button>
                                </Tooltip.Trigger>
                                <Tooltip.Portal>
                                    <Tooltip.Content
                                        className="px-3 py-2 text-xs text-white bg-gray-900 rounded-lg shadow-xl"
                                        sideOffset={5}
                                    >
                                        Available balance for calls
                                        <Tooltip.Arrow className="fill-gray-900" />
                                    </Tooltip.Content>
                                </Tooltip.Portal>
                            </Tooltip.Root>
                        </Tooltip.Provider>

                        {/* Add Funds */}
                        <button className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg shadow-sm shadow-blue-500/25 transition-all hover:-translate-y-0.5">
                            <Plus className="w-4 h-4" />
                            <span>Add funds</span>
                        </button>

                        {/* Notifications */}
                        <DropdownMenu.Root>
                            <DropdownMenu.Trigger asChild>
                                <button className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                                    <Bell className="w-5 h-5" />
                                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
                                </button>
                            </DropdownMenu.Trigger>
                            <DropdownMenu.Portal>
                                <DropdownMenu.Content
                                    className="w-80 p-2 bg-white border border-gray-200 rounded-xl shadow-xl"
                                    sideOffset={5}
                                    align="end"
                                >
                                    <div className="px-3 py-2 border-b border-gray-100">
                                        <h3 className="font-semibold text-gray-900">Notifications</h3>
                                        <p className="text-xs text-gray-500">You have 3 new notifications</p>
                                    </div>
                                    <div className="py-2 space-y-1">
                                        <NotificationItem
                                            title="New call completed"
                                            description="Agent finished call with +91812345..."
                                            time="2 min ago"
                                            isNew
                                        />
                                        <NotificationItem
                                            title="Batch completed"
                                            description="Campaign 'Welcome Calls' finished"
                                            time="1 hour ago"
                                            isNew
                                        />
                                        <NotificationItem
                                            title="Low balance warning"
                                            description="Your balance is below $10"
                                            time="3 hours ago"
                                        />
                                    </div>
                                    <div className="px-3 py-2 border-t border-gray-100">
                                        <a href="/dashboard/notifications" className="text-sm text-blue-500 hover:text-blue-600 font-medium">
                                            View all notifications →
                                        </a>
                                    </div>
                                </DropdownMenu.Content>
                            </DropdownMenu.Portal>
                        </DropdownMenu.Root>

                        {/* Help */}
                        <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                            <HelpCircle className="w-5 h-5" />
                        </button>

                        {/* Settings */}
                        <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
                            <Settings className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </header>
    );
}

function NotificationItem({
    title,
    description,
    time,
    isNew,
}: {
    title: string;
    description: string;
    time: string;
    isNew?: boolean;
}) {
    return (
        <button className="w-full flex items-start gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors text-left">
            {isNew && (
                <div className="w-2 h-2 mt-2 bg-blue-500 rounded-full shrink-0" />
            )}
            <div className={cn("flex-1", !isNew && "ml-5")}>
                <p className="text-sm font-medium text-gray-900">{title}</p>
                <p className="text-xs text-gray-500 truncate">{description}</p>
            </div>
            <span className="text-xs text-gray-400 shrink-0">{time}</span>
        </button>
    );
}

export default AdvancedHeader;
