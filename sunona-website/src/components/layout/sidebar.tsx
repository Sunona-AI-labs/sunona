/**
 * Sidebar Component
 * Sunona Dashboard Navigation
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
    Bot,
    Phone,
    History,
    Database,
    Layers,
    Mic2,
    Code2,
    Settings2,
    Workflow,
    Megaphone,
    FileText,
    Building2,
    Users,
    Receipt,
    Shield,
    CreditCard,
    LogOut,
    ChevronDown,
    ExternalLink,
    Wallet,
    HelpCircle,
} from "lucide-react";

interface SidebarLink {
    label: string;
    href: string;
    icon: React.ReactNode;
    external?: boolean;
}

interface SidebarSection {
    title?: string;
    links: SidebarLink[];
}

const platformSection: SidebarSection = {
    title: "Platform",
    links: [
        { label: "Agent Setup", href: "/dashboard/agents", icon: <Bot className="w-5 h-5" /> },
        { label: "Call History", href: "/dashboard/calls", icon: <History className="w-5 h-5" /> },
        { label: "My Numbers", href: "/dashboard/phone-numbers", icon: <Phone className="w-5 h-5" /> },
        { label: "Knowledge Base", href: "/dashboard/knowledge", icon: <Database className="w-5 h-5" /> },
        { label: "Batches", href: "/dashboard/batches", icon: <Layers className="w-5 h-5" /> },
        { label: "Voice Lab", href: "/dashboard/voice-lab", icon: <Mic2 className="w-5 h-5" /> },
        { label: "Developers", href: "/dashboard/developers", icon: <Code2 className="w-5 h-5" /> },
        { label: "Providers", href: "/dashboard/providers", icon: <Settings2 className="w-5 h-5" /> },
        { label: "Workflows", href: "/dashboard/workflows", icon: <Workflow className="w-5 h-5" /> },
        { label: "Campaigns", href: "/dashboard/campaigns", icon: <Megaphone className="w-5 h-5" /> },
        { label: "Billing", href: "/dashboard/billing", icon: <CreditCard className="w-5 h-5" /> },
        { label: "Documentation", href: "/docs", icon: <FileText className="w-5 h-5" />, external: true },
    ],
};

const workplaceLinks: SidebarLink[] = [
    { label: "Account Info", href: "/dashboard/settings/account", icon: <Building2 className="w-4 h-4" /> },
    { label: "Team Members", href: "/dashboard/settings/team", icon: <Users className="w-4 h-4" /> },
    { label: "Compliance", href: "/dashboard/settings/compliance", icon: <Shield className="w-4 h-4" /> },
    { label: "Invoices", href: "/dashboard/settings/invoices", icon: <Receipt className="w-4 h-4" /> },
    { label: "Sub Accounts", href: "/dashboard/settings/subaccounts", icon: <CreditCard className="w-4 h-4" /> },
];

export function Sidebar() {
    const pathname = usePathname();
    const [workplaceOpen, setWorkplaceOpen] = React.useState(false);

    const isActive = (href: string) => {
        if (href === "/dashboard/agents") {
            return pathname === "/dashboard" || pathname.startsWith("/dashboard/agents");
        }
        return pathname.startsWith(href);
    };

    return (
        <aside className="w-[260px] min-h-screen bg-[#0A0A0A] border-r border-white/10 flex flex-col">
            {/* Logo */}
            <div className="p-5 border-b border-white/10">
                <Link href="/dashboard" className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#00D4AA] to-[#00F5C8] flex items-center justify-center">
                        <Mic2 className="w-5 h-5 text-black" />
                    </div>
                    <span className="text-lg font-bold text-white">Sunona</span>
                </Link>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-3 overflow-y-auto">
                {/* Platform Section */}
                <div className="mb-6">
                    <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-[#6B6B6B]">
                        {platformSection.title}
                    </p>
                    <div className="space-y-0.5">
                        {platformSection.links.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                target={link.external ? "_blank" : undefined}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm",
                                    "transition-all duration-200",
                                    isActive(link.href)
                                        ? "bg-blue-500/15 text-blue-400"
                                        : "text-[#B0B0B0] hover:bg-white/5 hover:text-white"
                                )}
                            >
                                <span className={cn(
                                    "opacity-70",
                                    isActive(link.href) && "opacity-100"
                                )}>
                                    {link.icon}
                                </span>
                                <span className="flex-1">{link.label}</span>
                                {link.external && (
                                    <ExternalLink className="w-3.5 h-3.5 opacity-50" />
                                )}
                            </Link>
                        ))}
                    </div>
                </div>

                {/* Team Section */}
                <div className="mb-6">
                    <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-[#6B6B6B]">
                        Team
                    </p>

                    {/* Workplace Dropdown */}
                    <button
                        onClick={() => setWorkplaceOpen(!workplaceOpen)}
                        className={cn(
                            "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm",
                            "transition-all duration-200",
                            "text-[#B0B0B0] hover:bg-white/5 hover:text-white"
                        )}
                    >
                        <Building2 className="w-5 h-5 opacity-70" />
                        <span className="flex-1 text-left">Workplace</span>
                        <ChevronDown className={cn(
                            "w-4 h-4 transition-transform duration-200",
                            workplaceOpen && "rotate-180"
                        )} />
                    </button>

                    {workplaceOpen && (
                        <div className="ml-5 mt-1 space-y-0.5 border-l border-white/10 pl-3">
                            {workplaceLinks.map((link) => (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    className={cn(
                                        "flex items-center gap-2 px-3 py-2 rounded-lg text-sm",
                                        "transition-all duration-200",
                                        isActive(link.href)
                                            ? "bg-blue-500/15 text-blue-400"
                                            : "text-[#B0B0B0] hover:bg-white/5 hover:text-white"
                                    )}
                                >
                                    {link.icon}
                                    <span>{link.label}</span>
                                </Link>
                            ))}
                        </div>
                    )}
                </div>
            </nav>

            {/* Footer */}
            <div className="p-3 border-t border-white/10">
                <div className="flex items-center gap-3 px-3 py-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#00D4AA] to-[#00F5C8] flex items-center justify-center text-black font-semibold text-sm">
                        U
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">User</p>
                        <p className="text-xs text-[#6B6B6B] truncate">user@example.com</p>
                    </div>
                    <button className="p-2 rounded-lg text-[#6B6B6B] hover:text-white hover:bg-white/5 transition-colors">
                        <LogOut className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </aside>
    );
}

export function TopHeader({ balance = 5.00 }: { balance?: number }) {
    return (
        <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
            <div className="flex items-center gap-2">
                {/* Breadcrumb or page title - handled by individual pages */}
            </div>

            <div className="flex items-center gap-4">
                {/* Balance */}
                <div className="flex items-center gap-3">
                    <span className="text-sm text-gray-600">
                        Available balance: <span className="text-gray-900 font-semibold">${balance.toFixed(2)}</span>
                    </span>
                    <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-transparent border border-gray-300 text-sm text-gray-700 hover:bg-gray-50 transition-colors">
                        <Wallet className="w-4 h-4" />
                        Add more funds
                    </button>
                </div>

                {/* Help */}
                <button className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-900 transition-colors">
                    <HelpCircle className="w-4 h-4" />
                    <span>Help</span>
                </button>
            </div>
        </header>
    );
}
