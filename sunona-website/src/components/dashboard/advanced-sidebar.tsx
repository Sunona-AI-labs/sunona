/**
 * Advanced Dashboard Sidebar - 21st.dev Style
 * Collapsible, animated sidebar with dark theme and tooltips
 * Based on: https://21st.dev/uniquesonu/dashboard-with-collapsible-sidebar
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import * as Tooltip from "@radix-ui/react-tooltip";
import * as Collapsible from "@radix-ui/react-collapsible";
import { cn } from "@/lib/utils";
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
    Building2,
    ChevronLeft,
    ChevronRight,
    ChevronDown,
    LogOut,
    Moon,
    Sun,
    HelpCircle,
} from "lucide-react";

const platformNavItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Agents", href: "/dashboard/agents", icon: Bot },
    { name: "Call History", href: "/dashboard/calls", icon: PhoneCall },
    { name: "Phone Numbers", href: "/dashboard/phone-numbers", icon: Phone },
    { name: "Knowledge Base", href: "/dashboard/knowledge", icon: Database },
    { name: "Batches", href: "/dashboard/batches", icon: Layers },
    { name: "Voice Lab", href: "/dashboard/voice-lab", icon: Mic2 },
    { name: "Developers", href: "/dashboard/developers", icon: Code2 },
    { name: "Providers", href: "/dashboard/providers", icon: Plug },
    { name: "Workflows", href: "/dashboard/workflows", icon: Workflow },
    { name: "Campaigns", href: "/dashboard/campaigns", icon: Megaphone },
];

const analyticsNavItems = [
    { name: "Analytics", href: "/dashboard/analytics", icon: ChartBar },
    { name: "Recordings", href: "/dashboard/recordings", icon: FileAudio },
    { name: "Billing", href: "/dashboard/billing", icon: CreditCard },
];

const workplaceSubItems = [
    { name: "Account Info", href: "/dashboard/settings" },
    { name: "Team Members", href: "/dashboard/team" },
    { name: "Invoices", href: "/dashboard/invoices" },
];

export function AdvancedSidebar() {
    const pathname = usePathname();
    const [isCollapsed, setIsCollapsed] = React.useState(false);
    const [workplaceOpen, setWorkplaceOpen] = React.useState(false);
    const [isDark, setIsDark] = React.useState(true);

    const toggleTheme = () => {
        setIsDark(!isDark);
        document.documentElement.classList.toggle("dark");
    };

    return (
        <Tooltip.Provider delayDuration={0}>
            <aside
                className={cn(
                    "fixed left-0 top-0 z-40 h-screen flex flex-col",
                    "bg-[#0f0f14] border-r border-white/5",
                    "transition-all duration-300 ease-in-out",
                    isCollapsed ? "w-[68px]" : "w-[260px]"
                )}
            >
                {/* Header with Logo */}
                <div className={cn(
                    "flex items-center h-16 px-4 border-b border-white/5",
                    isCollapsed ? "justify-center" : "justify-between"
                )}>
                    <Link href="/dashboard" className="flex items-center gap-3">
                        <div className="relative flex items-center justify-center">
                            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-400 via-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/25">
                                <Mic2 className="w-5 h-5 text-white" />
                            </div>
                            <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 blur-md opacity-40 -z-10" />
                        </div>
                        {!isCollapsed && (
                            <span className="text-lg font-bold bg-gradient-to-r from-white to-gray-300 text-transparent bg-clip-text">
                                SUNONA
                            </span>
                        )}
                    </Link>

                    {/* Collapse Toggle */}
                    <button
                        onClick={() => setIsCollapsed(!isCollapsed)}
                        className={cn(
                            "p-1.5 rounded-lg",
                            "text-gray-400 hover:text-white",
                            "hover:bg-white/5 transition-all",
                            isCollapsed && "absolute -right-3 top-6 bg-[#0f0f14] border border-white/10 rounded-full shadow-lg"
                        )}
                    >
                        {isCollapsed ? (
                            <ChevronRight className="w-4 h-4" />
                        ) : (
                            <ChevronLeft className="w-4 h-4" />
                        )}
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-6 scrollbar-thin">
                    {/* Platform Section */}
                    <div>
                        {!isCollapsed && (
                            <h3 className="px-3 mb-2 text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                                Platform
                            </h3>
                        )}
                        <ul className="space-y-1">
                            {platformNavItems.map((item) => (
                                <NavItem
                                    key={item.name}
                                    item={item}
                                    isActive={pathname === item.href}
                                    isCollapsed={isCollapsed}
                                />
                            ))}
                        </ul>
                    </div>

                    {/* Analytics Section */}
                    <div>
                        {!isCollapsed && (
                            <h3 className="px-3 mb-2 text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                                Insights
                            </h3>
                        )}
                        <ul className="space-y-1">
                            {analyticsNavItems.map((item) => (
                                <NavItem
                                    key={item.name}
                                    item={item}
                                    isActive={pathname === item.href}
                                    isCollapsed={isCollapsed}
                                />
                            ))}
                        </ul>
                    </div>

                    {/* Workplace Section (Collapsible) */}
                    <div>
                        {!isCollapsed && (
                            <h3 className="px-3 mb-2 text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                                Workspace
                            </h3>
                        )}

                        <Collapsible.Root open={workplaceOpen} onOpenChange={setWorkplaceOpen}>
                            <Collapsible.Trigger asChild>
                                <button
                                    className={cn(
                                        "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg",
                                        "text-gray-400 hover:text-white hover:bg-white/5",
                                        "transition-all duration-200",
                                        isCollapsed && "justify-center"
                                    )}
                                >
                                    <Building2 className="w-[18px] h-[18px] shrink-0" />
                                    {!isCollapsed && (
                                        <>
                                            <span className="flex-1 text-left text-sm font-medium">Workplace</span>
                                            <ChevronDown
                                                className={cn(
                                                    "w-4 h-4 transition-transform duration-200",
                                                    workplaceOpen && "rotate-180"
                                                )}
                                            />
                                        </>
                                    )}
                                </button>
                            </Collapsible.Trigger>

                            <Collapsible.Content className="overflow-hidden data-[state=open]:animate-slideDown data-[state=closed]:animate-slideUp">
                                {!isCollapsed && (
                                    <ul className="ml-6 mt-1 space-y-1 border-l border-white/10 pl-3">
                                        {workplaceSubItems.map((item) => (
                                            <li key={item.name}>
                                                <Link
                                                    href={item.href}
                                                    className={cn(
                                                        "block px-3 py-2 text-sm rounded-lg",
                                                        "transition-all duration-200",
                                                        pathname === item.href
                                                            ? "text-cyan-400 bg-cyan-500/10"
                                                            : "text-gray-400 hover:text-white hover:bg-white/5"
                                                    )}
                                                >
                                                    {item.name}
                                                </Link>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </Collapsible.Content>
                        </Collapsible.Root>
                    </div>
                </nav>

                {/* Footer Actions */}
                <div className="border-t border-white/5 p-3 space-y-2">
                    {/* Theme Toggle */}
                    <button
                        onClick={toggleTheme}
                        className={cn(
                            "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg",
                            "text-gray-400 hover:text-white hover:bg-white/5",
                            "transition-all duration-200",
                            isCollapsed && "justify-center"
                        )}
                    >
                        {isDark ? (
                            <Sun className="w-[18px] h-[18px] shrink-0" />
                        ) : (
                            <Moon className="w-[18px] h-[18px] shrink-0" />
                        )}
                        {!isCollapsed && <span className="text-sm font-medium">Toggle Theme</span>}
                    </button>

                    {/* Help */}
                    <button
                        className={cn(
                            "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg",
                            "text-gray-400 hover:text-white hover:bg-white/5",
                            "transition-all duration-200",
                            isCollapsed && "justify-center"
                        )}
                    >
                        <HelpCircle className="w-[18px] h-[18px] shrink-0" />
                        {!isCollapsed && <span className="text-sm font-medium">Help & Support</span>}
                    </button>

                    {/* User Profile */}
                    <div className={cn(
                        "flex items-center gap-3 p-3 rounded-xl",
                        "bg-gradient-to-r from-white/5 to-transparent",
                        "border border-white/5",
                        isCollapsed && "justify-center p-2"
                    )}>
                        <div className="relative">
                            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-semibold text-sm">
                                U
                            </div>
                            <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-[#0f0f14]" />
                        </div>
                        {!isCollapsed && (
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-white truncate">User</p>
                                <p className="text-xs text-gray-500 truncate">Free Plan</p>
                            </div>
                        )}
                        {!isCollapsed && (
                            <Tooltip.Root>
                                <Tooltip.Trigger asChild>
                                    <button className="p-1.5 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all">
                                        <LogOut className="w-4 h-4" />
                                    </button>
                                </Tooltip.Trigger>
                                <Tooltip.Portal>
                                    <Tooltip.Content
                                        className="px-3 py-1.5 text-xs font-medium text-white bg-gray-900 rounded-lg shadow-xl"
                                        sideOffset={5}
                                    >
                                        Sign out
                                        <Tooltip.Arrow className="fill-gray-900" />
                                    </Tooltip.Content>
                                </Tooltip.Portal>
                            </Tooltip.Root>
                        )}
                    </div>
                </div>
            </aside>
        </Tooltip.Provider>
    );
}

// NavItem component with tooltip support
function NavItem({
    item,
    isActive,
    isCollapsed,
}: {
    item: { name: string; href: string; icon: React.ComponentType<{ className?: string }> };
    isActive: boolean;
    isCollapsed: boolean;
}) {
    const Icon = item.icon;

    const content = (
        <Link
            href={item.href}
            className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg",
                "transition-all duration-200",
                isCollapsed && "justify-center",
                isActive
                    ? "text-white bg-gradient-to-r from-cyan-500/20 to-blue-500/10 border border-cyan-500/20 shadow-lg shadow-cyan-500/5"
                    : "text-gray-400 hover:text-white hover:bg-white/5"
            )}
        >
            <Icon className={cn(
                "w-[18px] h-[18px] shrink-0",
                isActive && "text-cyan-400"
            )} />
            {!isCollapsed && (
                <span className="text-sm font-medium">{item.name}</span>
            )}
            {isActive && !isCollapsed && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            )}
        </Link>
    );

    if (isCollapsed) {
        return (
            <li>
                <Tooltip.Root>
                    <Tooltip.Trigger asChild>{content}</Tooltip.Trigger>
                    <Tooltip.Portal>
                        <Tooltip.Content
                            className="px-3 py-1.5 text-xs font-medium text-white bg-gray-900 rounded-lg shadow-xl border border-white/10"
                            side="right"
                            sideOffset={10}
                        >
                            {item.name}
                            <Tooltip.Arrow className="fill-gray-900" />
                        </Tooltip.Content>
                    </Tooltip.Portal>
                </Tooltip.Root>
            </li>
        );
    }

    return <li>{content}</li>;
}

export default AdvancedSidebar;
