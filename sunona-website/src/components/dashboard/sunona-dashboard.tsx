/**
 * Sunona Dashboard - 21st.dev Style
 * Professional collapsible sidebar dashboard with stats cards
 * Based on: https://21st.dev/uniquesonu/dashboard-with-collapsible-sidebar
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    LayoutDashboard,
    Bot,
    PhoneCall,
    Phone,
    Database,
    Layers,
    Mic2,
    Code2,
    Plug,
    Workflow,
    Megaphone,
    ChartBar,
    FileAudio,
    CreditCard,
    Settings,
    Users,
    HelpCircle,
    ChevronLeft,
    ChevronRight,
    ChevronDown,
    LogOut,
    Moon,
    Sun,
    Search,
    Bell,
    Wallet,
    Plus,
    TrendingUp,
    TrendingDown,
    Clock,
    DollarSign,
    Activity,
    Eye,
    EyeOff,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Navigation items for Sunona Voice AI
const navigationItems = [
    { icon: LayoutDashboard, label: "Dashboard", href: "/dashboard", notifications: 0 },
    { icon: Bot, label: "Agents", href: "/dashboard/agents", notifications: 3 },
    { icon: PhoneCall, label: "Call History", href: "/dashboard/calls", notifications: 12 },
    { icon: Phone, label: "Phone Numbers", href: "/dashboard/phone-numbers", notifications: 0 },
    { icon: Database, label: "Knowledge Base", href: "/dashboard/knowledge", notifications: 0 },
    { icon: Layers, label: "Batches", href: "/dashboard/batches", notifications: 0 },
    { icon: Mic2, label: "Voice Lab", href: "/dashboard/voice-lab", notifications: 0 },
    { icon: Code2, label: "Developers", href: "/dashboard/developers", notifications: 0 },
    { icon: Plug, label: "Providers", href: "/dashboard/providers", notifications: 0 },
    { icon: Workflow, label: "Workflows", href: "/dashboard/workflows", notifications: 0 },
    { icon: Megaphone, label: "Campaigns", href: "/dashboard/campaigns", notifications: 0 },
];

const accountItems = [
    { icon: Settings, label: "Settings", href: "/dashboard/settings" },
    { icon: HelpCircle, label: "Help & Support", href: "/dashboard/help" },
];

// Stats data for Sunona (costs based on $0.04/min rate)
const statsData = [
    {
        title: "Total Calls",
        value: "2,847",
        change: "+12%",
        trend: "up",
        icon: PhoneCall,
        color: "blue",
    },
    {
        title: "Active Agents",
        value: "12",
        change: "+3",
        trend: "up",
        icon: Bot,
        color: "green",
    },
    {
        title: "Minutes Used",
        value: "4,521",
        change: "+8%",
        trend: "up",
        icon: Clock,
        color: "purple",
    },
    {
        title: "Total Spent",
        value: "$180.84",  // 4,521 mins × $0.04 = $180.84
        change: "-15%",
        trend: "down",
        icon: DollarSign,
        color: "amber",
    },
];

// Recent activity data (costs based on $0.04/min rate)
const recentActivity = [
    { id: "call_001", agent: "Customer Support", user: "+91812345678", duration: "2:45", status: "completed", cost: "$0.11", time: "2 min ago" },
    { id: "call_002", agent: "Sales Outreach", user: "+91987654321", duration: "5:12", status: "completed", cost: "$0.21", time: "5 min ago" },
    { id: "call_003", agent: "Recruiter AI", user: "+91765432100", duration: "1:30", status: "no-answer", cost: "$0.06", time: "12 min ago" },
    { id: "call_004", agent: "Customer Support", user: "+91654321098", duration: "3:22", status: "completed", cost: "$0.13", time: "18 min ago" },
    { id: "call_005", agent: "Welcome Agent", user: "+91543210987", duration: "4:05", status: "completed", cost: "$0.16", time: "25 min ago" },
];

export default function SunonaDashboard() {
    const pathname = usePathname();
    const [sidebarOpen, setSidebarOpen] = React.useState(true);
    const [darkMode, setDarkMode] = React.useState(false);

    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
        document.documentElement.classList.toggle("dark");
    };

    return (
        <div
            className={cn(
                "dashboard-container min-h-screen flex",
                darkMode && "dark-mode"
            )}
        >

            {/* Sidebar */}
            <nav
                className={cn(
                    "fixed top-0 left-0 h-screen shrink-0 border-r transition-all duration-300 ease-in-out z-30",
                    sidebarOpen ? "w-64" : "w-16",
                    darkMode
                        ? "border-gray-800 bg-gray-900"
                        : "border-gray-200 bg-white",
                    "p-2 shadow-sm"
                )}
            >

                {/* Logo Section */}
                <div className={cn(
                    "flex items-center justify-between rounded-lg p-2 mb-4",
                    darkMode ? "bg-gray-800" : "bg-gray-50"
                )}>
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-lg">
                            <Mic2 className="w-5 h-5 text-white" />
                        </div>
                        {sidebarOpen && (
                            <span className={cn(
                                "font-bold text-lg",
                                darkMode ? "text-white" : "text-gray-900"
                            )}>
                                SUNONA
                            </span>
                        )}
                    </div>
                    <button
                        onClick={() => setSidebarOpen(!sidebarOpen)}
                        className={cn(
                            "p-1.5 rounded-lg transition-colors",
                            darkMode
                                ? "hover:bg-gray-700 text-gray-400"
                                : "hover:bg-gray-200 text-gray-600"
                        )}
                    >
                        {sidebarOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
                    </button>
                </div>

                {/* Navigation */}
                <div className="space-y-1">
                    {navigationItems.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 relative group",
                                    isActive
                                        ? darkMode
                                            ? "bg-blue-600 text-white"
                                            : "bg-blue-500 text-white"
                                        : darkMode
                                            ? "text-gray-400 hover:text-white hover:bg-gray-800"
                                            : "text-gray-600 hover:text-gray-900 hover:bg-gray-100",
                                    !sidebarOpen && "justify-center"
                                )}
                            >
                                <item.icon size={20} className="shrink-0" />
                                {sidebarOpen && (
                                    <>
                                        <span className="flex-1 text-sm font-medium">{item.label}</span>
                                        {item.notifications > 0 && (
                                            <span className={cn(
                                                "px-2 py-0.5 text-xs font-medium rounded-full",
                                                isActive
                                                    ? "bg-white/20 text-white"
                                                    : "bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300"
                                            )}>
                                                {item.notifications}
                                            </span>
                                        )}
                                    </>
                                )}
                                {/* Tooltip for collapsed state */}
                                {!sidebarOpen && (
                                    <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50">
                                        {item.label}
                                    </div>
                                )}
                            </Link>
                        );
                    })}
                </div>

                {/* Account Section */}
                {sidebarOpen && (
                    <div className={cn(
                        "mt-6 pt-4 border-t",
                        darkMode ? "border-gray-800" : "border-gray-200"
                    )}>
                        <p className={cn(
                            "px-3 mb-2 text-xs font-semibold uppercase tracking-wider",
                            darkMode ? "text-gray-500" : "text-gray-400"
                        )}>
                            Account
                        </p>
                        {accountItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors",
                                    darkMode
                                        ? "text-gray-400 hover:text-white hover:bg-gray-800"
                                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                                )}
                            >
                                <item.icon size={20} />
                                <span className="text-sm font-medium">{item.label}</span>
                            </Link>
                        ))}
                    </div>
                )}

                {/* User Profile */}
                <div className={cn(
                    "absolute bottom-4 left-2 right-2 p-3 rounded-lg",
                    darkMode ? "bg-gray-800" : "bg-gray-50"
                )}>
                    <div className={cn(
                        "flex items-center gap-3",
                        !sidebarOpen && "justify-center"
                    )}>
                        <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold text-sm">
                            U
                        </div>
                        {sidebarOpen && (
                            <div className="flex-1 min-w-0">
                                <p className={cn(
                                    "text-sm font-medium truncate",
                                    darkMode ? "text-white" : "text-gray-900"
                                )}>
                                    Demo User
                                </p>
                                <p className={cn(
                                    "text-xs truncate",
                                    darkMode ? "text-gray-400" : "text-gray-500"
                                )}>
                                    Free Plan
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main className={cn(
                "flex-1 overflow-auto transition-all duration-300",
                sidebarOpen ? "ml-64" : "ml-16"
            )}>
                {/* Header */}
                <header className={cn(
                    "sticky top-0 z-20 border-b",
                    darkMode
                        ? "bg-gray-800 border-gray-700"
                        : "bg-white border-gray-200"
                )}>

                    <div className="flex items-center justify-between px-6 h-16">
                        {/* Page Title */}
                        <div>
                            <h1 className={cn(
                                "text-xl font-bold",
                                darkMode ? "text-white" : "text-gray-900"
                            )}>
                                Dashboard
                            </h1>
                            <p className={cn(
                                "text-sm",
                                darkMode ? "text-gray-400" : "text-gray-500"
                            )}>
                                Welcome back to your dashboard
                            </p>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-3">
                            {/* Search */}
                            <div className={cn(
                                "relative hidden md:flex items-center",
                            )}>
                                <Search className={cn(
                                    "absolute left-3 w-4 h-4",
                                    darkMode ? "text-gray-500" : "text-gray-400"
                                )} />
                                <input
                                    type="text"
                                    placeholder="Search..."
                                    className={cn(
                                        "w-64 pl-9 pr-4 py-2 text-sm rounded-lg border transition-colors",
                                        darkMode
                                            ? "bg-gray-800 border-gray-700 text-white placeholder:text-gray-500 focus:border-blue-500"
                                            : "bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 focus:border-blue-500",
                                        "focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                                    )}
                                />
                            </div>

                            {/* Balance */}
                            <div className={cn(
                                "flex items-center gap-2 px-3 py-1.5 rounded-lg",
                                darkMode
                                    ? "bg-emerald-900/50 border border-emerald-700"
                                    : "bg-emerald-50 border border-emerald-200"
                            )}>
                                <Wallet className={cn(
                                    "w-4 h-4",
                                    darkMode ? "text-emerald-400" : "text-emerald-600"
                                )} />
                                <span className={cn(
                                    "text-sm font-medium",
                                    darkMode ? "text-emerald-400" : "text-emerald-700"
                                )}>
                                    $5.00
                                </span>
                            </div>

                            {/* Add Funds */}
                            <button className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg shadow-sm transition-colors">
                                <Plus className="w-4 h-4" />
                                <span>Add funds</span>
                            </button>

                            {/* Theme Toggle */}
                            <button
                                onClick={toggleDarkMode}
                                className={cn(
                                    "p-2 rounded-lg transition-colors",
                                    darkMode
                                        ? "hover:bg-gray-800 text-gray-400"
                                        : "hover:bg-gray-100 text-gray-600"
                                )}
                            >
                                {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                            </button>

                            {/* Notifications */}
                            <button className={cn(
                                "relative p-2 rounded-lg transition-colors",
                                darkMode
                                    ? "hover:bg-gray-800 text-gray-400"
                                    : "hover:bg-gray-100 text-gray-600"
                            )}>
                                <Bell size={20} />
                                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
                            </button>
                        </div>
                    </div>
                </header>

                {/* Dashboard Content */}
                <div className="p-6 space-y-6">
                    {/* Stats Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {statsData.map((stat, index) => (
                            <div
                                key={index}
                                className={cn(
                                    "p-6 rounded-xl border transition-all hover:shadow-lg",
                                    darkMode
                                        ? "bg-gray-800 border-gray-700 hover:border-gray-600"
                                        : "bg-white border-gray-200 hover:border-gray-300"
                                )}
                            >
                                <div className="flex items-center justify-between mb-4">
                                    <div className={cn(
                                        "p-2.5 rounded-lg",
                                        stat.color === "blue" && (darkMode ? "bg-blue-900/50" : "bg-blue-100"),
                                        stat.color === "green" && (darkMode ? "bg-green-900/50" : "bg-green-100"),
                                        stat.color === "purple" && (darkMode ? "bg-purple-900/50" : "bg-purple-100"),
                                        stat.color === "amber" && (darkMode ? "bg-amber-900/50" : "bg-amber-100"),
                                    )}>
                                        <stat.icon className={cn(
                                            "w-5 h-5",
                                            stat.color === "blue" && (darkMode ? "text-blue-400" : "text-blue-600"),
                                            stat.color === "green" && (darkMode ? "text-green-400" : "text-green-600"),
                                            stat.color === "purple" && (darkMode ? "text-purple-400" : "text-purple-600"),
                                            stat.color === "amber" && (darkMode ? "text-amber-400" : "text-amber-600"),
                                        )} />
                                    </div>
                                    <div className={cn(
                                        "flex items-center gap-1 text-xs font-medium",
                                        stat.trend === "up" ? "text-green-500" : "text-red-500"
                                    )}>
                                        {stat.trend === "up" ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                        {stat.change}
                                    </div>
                                </div>
                                <p className={cn(
                                    "text-2xl font-bold mb-1",
                                    darkMode ? "text-white" : "text-gray-900"
                                )}>
                                    {stat.value}
                                </p>
                                <p className={cn(
                                    "text-sm",
                                    darkMode ? "text-gray-400" : "text-gray-500"
                                )}>
                                    {stat.title}
                                </p>
                            </div>
                        ))}
                    </div>

                    {/* Recent Activity Table */}
                    <div className={cn(
                        "rounded-xl border overflow-hidden",
                        darkMode
                            ? "bg-gray-800 border-gray-700"
                            : "bg-white border-gray-200"
                    )}>
                        <div className="px-6 py-4 border-b flex items-center justify-between"
                            style={{ borderColor: darkMode ? "#374151" : "#e5e7eb" }}
                        >
                            <div>
                                <h2 className={cn(
                                    "text-lg font-semibold",
                                    darkMode ? "text-white" : "text-gray-900"
                                )}>
                                    Recent Activity
                                </h2>
                                <p className={cn(
                                    "text-sm",
                                    darkMode ? "text-gray-400" : "text-gray-500"
                                )}>
                                    Your latest call activity
                                </p>
                            </div>
                            <Link
                                href="/dashboard/calls"
                                className="text-sm text-blue-500 hover:text-blue-600 font-medium"
                            >
                                View all →
                            </Link>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className={cn(
                                        darkMode ? "bg-gray-700/50" : "bg-gray-50"
                                    )}>
                                        <th className={cn(
                                            "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider",
                                            darkMode ? "text-gray-400" : "text-gray-500"
                                        )}>
                                            Call ID
                                        </th>
                                        <th className={cn(
                                            "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider",
                                            darkMode ? "text-gray-400" : "text-gray-500"
                                        )}>
                                            Agent
                                        </th>
                                        <th className={cn(
                                            "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider",
                                            darkMode ? "text-gray-400" : "text-gray-500"
                                        )}>
                                            User
                                        </th>
                                        <th className={cn(
                                            "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider",
                                            darkMode ? "text-gray-400" : "text-gray-500"
                                        )}>
                                            Duration
                                        </th>
                                        <th className={cn(
                                            "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider",
                                            darkMode ? "text-gray-400" : "text-gray-500"
                                        )}>
                                            Status
                                        </th>
                                        <th className={cn(
                                            "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider",
                                            darkMode ? "text-gray-400" : "text-gray-500"
                                        )}>
                                            Cost
                                        </th>
                                        <th className={cn(
                                            "px-6 py-3 text-left text-xs font-medium uppercase tracking-wider",
                                            darkMode ? "text-gray-400" : "text-gray-500"
                                        )}>
                                            Time
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y" style={{
                                    borderColor: darkMode ? "#374151" : "#e5e7eb"
                                }}>
                                    {recentActivity.map((activity) => (
                                        <tr
                                            key={activity.id}
                                            className={cn(
                                                "transition-colors",
                                                darkMode
                                                    ? "hover:bg-gray-700/50"
                                                    : "hover:bg-gray-50"
                                            )}
                                        >
                                            <td className={cn(
                                                "px-6 py-4 text-sm font-mono",
                                                darkMode ? "text-gray-300" : "text-gray-900"
                                            )}>
                                                {activity.id}
                                            </td>
                                            <td className={cn(
                                                "px-6 py-4 text-sm",
                                                darkMode ? "text-gray-300" : "text-gray-900"
                                            )}>
                                                {activity.agent}
                                            </td>
                                            <td className={cn(
                                                "px-6 py-4 text-sm font-mono",
                                                darkMode ? "text-gray-400" : "text-gray-500"
                                            )}>
                                                {activity.user}
                                            </td>
                                            <td className={cn(
                                                "px-6 py-4 text-sm",
                                                darkMode ? "text-gray-300" : "text-gray-900"
                                            )}>
                                                {activity.duration}
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={cn(
                                                    "px-2 py-1 text-xs font-medium rounded-full",
                                                    activity.status === "completed"
                                                        ? "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-400"
                                                        : "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-400"
                                                )}>
                                                    {activity.status}
                                                </span>
                                            </td>
                                            <td className={cn(
                                                "px-6 py-4 text-sm font-medium",
                                                darkMode ? "text-gray-300" : "text-gray-900"
                                            )}>
                                                {activity.cost}
                                            </td>
                                            <td className={cn(
                                                "px-6 py-4 text-sm",
                                                darkMode ? "text-gray-400" : "text-gray-500"
                                            )}>
                                                {activity.time}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
