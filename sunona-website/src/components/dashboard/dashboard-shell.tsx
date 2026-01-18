/**
 * Shared Dashboard Layout - 21st.dev Style
 * Responsive layout with collapsible sidebar
 * Auto-adjusts for mobile, tablet, and desktop
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
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
    Settings,
    HelpCircle,
    ChevronLeft,
    ChevronRight,
    Moon,
    Sun,
    Search,
    Bell,
    Wallet,
    Plus,
    LogOut,
    Menu,
    X,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/lib/store/auth-store";

// Sidebar width constants (in pixels)
const SIDEBAR_OPEN_WIDTH = 256; // 16rem = 256px
const SIDEBAR_CLOSED_WIDTH = 64; // 4rem = 64px

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

// Route title mapping
const routeTitles: Record<string, { title: string; subtitle: string }> = {
    "/dashboard": { title: "Dashboard", subtitle: "Overview of your Voice AI platform" },
    "/dashboard/agents": { title: "Agents", subtitle: "Configure and manage your AI agents" },
    "/dashboard/calls": { title: "Call History", subtitle: "View all agent conversations" },
    "/dashboard/phone-numbers": { title: "Phone Numbers", subtitle: "Manage your telephony numbers" },
    "/dashboard/knowledge": { title: "Knowledge Base", subtitle: "Upload and manage RAG documents" },
    "/dashboard/batches": { title: "Batches", subtitle: "Run bulk calling campaigns" },
    "/dashboard/voice-lab": { title: "Voice Lab", subtitle: "Explore and customize voices" },
    "/dashboard/developers": { title: "Developers", subtitle: "API keys and integrations" },
    "/dashboard/providers": { title: "Providers", subtitle: "Connect external AI providers" },
    "/dashboard/workflows": { title: "Workflows", subtitle: "Automate call workflows" },
    "/dashboard/campaigns": { title: "Campaigns", subtitle: "Manage marketing campaigns" },
    "/dashboard/settings": { title: "Settings", subtitle: "Account preferences" },
    "/dashboard/billing": { title: "Billing", subtitle: "Manage payments and invoices" },
    "/dashboard/analytics": { title: "Analytics", subtitle: "View insights and metrics" },
};

interface DashboardShellProps {
    children: React.ReactNode;
}

export function DashboardShell({ children }: DashboardShellProps) {
    const pathname = usePathname();
    const router = useRouter();
    const logout = useAuthStore((state) => state.logout);
    const user = useAuthStore((state) => state.user);
    const wallet = useAuthStore((state) => state.wallet);

    // Sidebar states
    const [sidebarOpen, setSidebarOpen] = React.useState(true);
    const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);
    const [darkMode, setDarkMode] = React.useState(false);

    const pageInfo = routeTitles[pathname] || { title: "Dashboard", subtitle: "Welcome" };

    // Close mobile menu on route change
    React.useEffect(() => {
        setMobileMenuOpen(false);
    }, [pathname]);

    // Close mobile menu on window resize to desktop
    React.useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth >= 1024) {
                setMobileMenuOpen(false);
            }
        };
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    const toggleDarkMode = () => {
        setDarkMode(!darkMode);
    };

    const handleLogout = () => {
        logout();
        router.push("/login");
    };

    // Calculate main content margin based on sidebar state
    const mainContentStyle = {
        marginLeft: sidebarOpen ? `${SIDEBAR_OPEN_WIDTH}px` : `${SIDEBAR_CLOSED_WIDTH}px`,
        transition: "margin-left 300ms ease-in-out",
    };

    return (
        <div
            className={cn(
                "dashboard-container min-h-screen",
                darkMode && "dark-mode"
            )}
        >
            {/* Mobile Overlay */}
            {mobileMenuOpen && (
                <div
                    className="fixed inset-0 bg-black/50 z-40 lg:hidden"
                    onClick={() => setMobileMenuOpen(false)}
                />
            )}

            {/* Sidebar - Desktop */}
            <nav
                className={cn(
                    "fixed top-0 left-0 h-screen border-r z-30 hidden lg:block",
                    "transition-all duration-300 ease-in-out",
                    darkMode
                        ? "border-gray-800 bg-gray-900"
                        : "border-gray-200 bg-white",
                    "shadow-sm"
                )}
                style={{ width: sidebarOpen ? SIDEBAR_OPEN_WIDTH : SIDEBAR_CLOSED_WIDTH }}
            >
                <div className="p-2 h-full flex flex-col">
                    {/* Logo Section */}
                    <div className={cn(
                        "flex items-center justify-between rounded-lg p-2 mb-4",
                        darkMode ? "bg-gray-800" : "bg-gray-50"
                    )}>
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-lg flex-shrink-0">
                                <Mic2 className="w-5 h-5 text-white" />
                            </div>
                            {sidebarOpen && (
                                <span className={cn(
                                    "font-bold text-lg whitespace-nowrap",
                                    darkMode ? "text-white" : "text-gray-900"
                                )}>
                                    SUNONA
                                </span>
                            )}
                        </div>
                        <button
                            onClick={() => setSidebarOpen(!sidebarOpen)}
                            className={cn(
                                "p-1.5 rounded-lg transition-colors flex-shrink-0",
                                darkMode
                                    ? "hover:bg-gray-700 text-gray-400"
                                    : "hover:bg-gray-200 text-gray-600"
                            )}
                        >
                            {sidebarOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
                        </button>
                    </div>

                    {/* Navigation */}
                    <div className="flex-1 overflow-y-auto space-y-1">
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
                                        !sidebarOpen && "justify-center px-2"
                                    )}
                                >
                                    <item.icon size={20} className="flex-shrink-0" />
                                    {sidebarOpen && (
                                        <>
                                            <span className="flex-1 text-sm font-medium truncate">{item.label}</span>
                                            {item.notifications > 0 && (
                                                <span className={cn(
                                                    "px-2 py-0.5 text-xs font-medium rounded-full flex-shrink-0",
                                                    isActive
                                                        ? "bg-white/20 text-white"
                                                        : "bg-blue-100 text-blue-600"
                                                )}>
                                                    {item.notifications}
                                                </span>
                                            )}
                                        </>
                                    )}
                                    {/* Tooltip for collapsed state */}
                                    {!sidebarOpen && (
                                        <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 shadow-lg">
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
                            "pt-4 border-t mt-4",
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
                        "mt-4 p-3 rounded-lg",
                        darkMode ? "bg-gray-800" : "bg-gray-100"
                    )}>
                        <div className={cn(
                            "flex items-center gap-3",
                            !sidebarOpen && "justify-center"
                        )}>
                            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
                                {user?.name?.charAt(0) || "U"}
                            </div>
                            {sidebarOpen && (
                                <>
                                    <div className="flex-1 min-w-0">
                                        <p className={cn(
                                            "text-sm font-medium truncate",
                                            darkMode ? "text-white" : "text-gray-900"
                                        )}>
                                            {user?.name || "Demo User"}
                                        </p>
                                        <p className={cn(
                                            "text-xs truncate",
                                            darkMode ? "text-gray-400" : "text-gray-500"
                                        )}>
                                            {user?.tier || "Free"} Plan
                                        </p>
                                    </div>
                                    <button
                                        onClick={handleLogout}
                                        className={cn(
                                            "p-1.5 rounded-lg transition-colors flex-shrink-0",
                                            darkMode
                                                ? "hover:bg-gray-700 text-gray-400 hover:text-red-400"
                                                : "hover:bg-gray-200 text-gray-500 hover:text-red-600"
                                        )}
                                    >
                                        <LogOut size={16} />
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </nav>

            {/* Sidebar - Mobile */}
            <nav
                className={cn(
                    "fixed top-0 left-0 h-screen w-64 border-r z-50 lg:hidden",
                    "transform transition-transform duration-300 ease-in-out",
                    mobileMenuOpen ? "translate-x-0" : "-translate-x-full",
                    darkMode
                        ? "border-gray-800 bg-gray-900"
                        : "border-gray-200 bg-white",
                    "shadow-xl"
                )}
            >
                <div className="p-4 h-full flex flex-col">
                    {/* Mobile Header */}
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-lg">
                                <Mic2 className="w-5 h-5 text-white" />
                            </div>
                            <span className={cn(
                                "font-bold text-lg",
                                darkMode ? "text-white" : "text-gray-900"
                            )}>
                                SUNONA
                            </span>
                        </div>
                        <button
                            onClick={() => setMobileMenuOpen(false)}
                            className={cn(
                                "p-2 rounded-lg",
                                darkMode
                                    ? "hover:bg-gray-800 text-gray-400"
                                    : "hover:bg-gray-100 text-gray-600"
                            )}
                        >
                            <X size={20} />
                        </button>
                    </div>

                    {/* Mobile Navigation */}
                    <div className="flex-1 overflow-y-auto space-y-1">
                        {navigationItems.map((item) => {
                            const isActive = pathname === item.href;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={cn(
                                        "flex items-center gap-3 px-3 py-3 rounded-lg transition-colors",
                                        isActive
                                            ? darkMode
                                                ? "bg-blue-600 text-white"
                                                : "bg-blue-500 text-white"
                                            : darkMode
                                                ? "text-gray-400 hover:text-white hover:bg-gray-800"
                                                : "text-gray-600 hover:text-gray-900 hover:bg-gray-100",
                                    )}
                                >
                                    <item.icon size={20} />
                                    <span className="text-sm font-medium">{item.label}</span>
                                    {item.notifications > 0 && (
                                        <span className={cn(
                                            "ml-auto px-2 py-0.5 text-xs font-medium rounded-full",
                                            isActive
                                                ? "bg-white/20 text-white"
                                                : "bg-blue-100 text-blue-600"
                                        )}>
                                            {item.notifications}
                                        </span>
                                    )}
                                </Link>
                            );
                        })}
                    </div>

                    {/* Mobile User Profile */}
                    <div className={cn(
                        "mt-4 p-3 rounded-lg",
                        darkMode ? "bg-gray-800" : "bg-gray-100"
                    )}>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold">
                                {user?.name?.charAt(0) || "U"}
                            </div>
                            <div className="flex-1">
                                <p className={cn(
                                    "font-medium",
                                    darkMode ? "text-white" : "text-gray-900"
                                )}>
                                    {user?.name || "Demo User"}
                                </p>
                                <p className={cn(
                                    "text-xs",
                                    darkMode ? "text-gray-400" : "text-gray-500"
                                )}>
                                    {user?.email || "demo@sunona.ai"}
                                </p>
                            </div>
                            <button
                                onClick={handleLogout}
                                className={cn(
                                    "p-2 rounded-lg",
                                    darkMode
                                        ? "hover:bg-gray-700 text-red-400"
                                        : "hover:bg-gray-200 text-red-600"
                                )}
                            >
                                <LogOut size={18} />
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Main Content */}
            <main
                className="min-h-screen lg:block"
                style={mainContentStyle}
            >
                {/* Add responsive margin for mobile/tablet */}
                <style jsx>{`
                    @media (max-width: 1023px) {
                        main {
                            margin-left: 0 !important;
                        }
                    }
                `}</style>

                {/* Header */}
                <header className={cn(
                    "sticky top-0 z-20 border-b",
                    darkMode
                        ? "bg-gray-800 border-gray-700"
                        : "bg-white border-gray-200"
                )}>
                    <div className="flex items-center justify-between px-4 lg:px-6 h-16">
                        {/* Mobile Menu Button */}
                        <button
                            onClick={() => setMobileMenuOpen(true)}
                            className={cn(
                                "p-2 rounded-lg lg:hidden",
                                darkMode
                                    ? "hover:bg-gray-700 text-gray-400"
                                    : "hover:bg-gray-100 text-gray-600"
                            )}
                        >
                            <Menu size={20} />
                        </button>

                        {/* Page Title */}
                        <div className="flex-1 lg:flex-none">
                            <h1 className={cn(
                                "text-lg lg:text-xl font-bold",
                                darkMode ? "text-white" : "text-gray-900"
                            )}>
                                {pageInfo.title}
                            </h1>
                            <p className={cn(
                                "text-xs lg:text-sm hidden sm:block",
                                darkMode ? "text-gray-400" : "text-gray-500"
                            )}>
                                {pageInfo.subtitle}
                            </p>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-2 lg:gap-3">
                            {/* Search - Hidden on mobile */}
                            <div className="relative hidden xl:flex items-center">
                                <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none z-10" style={{ paddingLeft: '14px' }}>
                                    <Search className="w-4 h-4 text-gray-400" />
                                </div>
                                <input
                                    type="text"
                                    placeholder="Search..."
                                    style={{ paddingLeft: '40px' }}
                                    className={cn(
                                        "w-48 2xl:w-64 pr-4 py-2.5 text-sm rounded-xl border transition-all duration-200",
                                        darkMode
                                            ? "bg-gray-700 border-gray-600 text-white placeholder:text-gray-400 hover:border-gray-500 focus:bg-gray-600"
                                            : "bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400 hover:border-gray-300 hover:bg-gray-100 focus:bg-white",
                                        "focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
                                    )}
                                />
                            </div>




                            {/* Balance - Compact on small screens */}
                            <div className={cn(
                                "hidden sm:flex items-center gap-2 px-2 lg:px-3 py-1.5 rounded-lg",
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
                                    ${wallet?.balance?.toFixed(2) || "5.00"}
                                </span>
                            </div>

                            {/* Add Funds - Icon only on mobile */}
                            <button className="flex items-center gap-1.5 px-2 lg:px-3 py-1.5 bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium rounded-lg shadow-sm transition-colors">
                                <Plus className="w-4 h-4" />
                                <span className="hidden lg:inline">Add funds</span>
                            </button>

                            {/* Theme Toggle */}
                            <button
                                onClick={toggleDarkMode}
                                className={cn(
                                    "p-2 rounded-lg transition-colors",
                                    darkMode
                                        ? "hover:bg-gray-700 text-gray-400"
                                        : "hover:bg-gray-100 text-gray-600"
                                )}
                            >
                                {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                            </button>

                            {/* Notifications */}
                            <button className={cn(
                                "relative p-2 rounded-lg transition-colors",
                                darkMode
                                    ? "hover:bg-gray-700 text-gray-400"
                                    : "hover:bg-gray-100 text-gray-600"
                            )}>
                                <Bell size={20} />
                                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
                            </button>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <div className="p-4 lg:p-6">
                    {children}
                </div>
            </main>
        </div>
    );
}

export default DashboardShell;
