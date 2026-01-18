/**
 * Navbar Component
 * Sunona-style navigation with multiple links
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
    Menu,
    X,
    Zap,
    ChevronDown,
    ExternalLink,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface NavItem {
    label: string;
    href: string;
    external?: boolean;
    hasDropdown?: boolean;
}

const navItems: NavItem[] = [
    { label: "How it Works", href: "/#how-it-works" },
    { label: "Agents", href: "/dashboard/agents" },
    { label: "Features", href: "/features" },
    { label: "Case Studies", href: "/use-cases" },
    { label: "Pricing", href: "/pricing" },
    { label: "Documentation", href: "/docs", hasDropdown: true },
    { label: "Careers", href: "#", external: true, hasDropdown: true },
];

export function Navbar() {
    const pathname = usePathname();
    const [isScrolled, setIsScrolled] = React.useState(false);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);

    // Handle scroll effect
    React.useEffect(() => {
        const handleScroll = () => {
            setIsScrolled(window.scrollY > 50);
        };

        window.addEventListener("scroll", handleScroll);
        return () => window.removeEventListener("scroll", handleScroll);
    }, []);

    // Close mobile menu on route change
    React.useEffect(() => {
        setIsMobileMenuOpen(false);
    }, [pathname]);

    // Prevent body scroll when mobile menu is open
    React.useEffect(() => {
        if (isMobileMenuOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "";
        }
        return () => {
            document.body.style.overflow = "";
        };
    }, [isMobileMenuOpen]);

    const isActive = (href: string) => {
        if (href === "/") return pathname === "/";
        if (href.startsWith("/#")) return false;
        return pathname.startsWith(href);
    };

    return (
        <header
            className={cn(
                "fixed top-8 left-0 right-0 z-50 transition-all duration-300",
                isScrolled
                    ? "bg-[#0a0a0f]/95 backdrop-blur-xl border-b border-white/[0.05]"
                    : "bg-transparent"
            )}
        >
            <nav className="container-custom">
                <div className="flex items-center justify-between h-14">
                    {/* Logo */}
                    <Link
                        href="/"
                        className="flex items-center gap-2 group"
                    >
                        <div className="relative">
                            <div className="absolute inset-0 bg-cyan-500 rounded blur-lg opacity-30 group-hover:opacity-50 transition-opacity" />
                            <div className="relative bg-gradient-to-br from-cyan-400 to-cyan-600 rounded p-1.5">
                                <Zap className="h-4 w-4 text-black" />
                            </div>
                        </div>
                        <span className="text-lg font-bold text-white tracking-tight">
                            Sunona
                        </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="hidden lg:flex items-center gap-1">
                        {navItems.map((item) => (
                            <Link
                                key={item.href}
                                href={item.href}
                                target={item.external ? "_blank" : undefined}
                                rel={item.external ? "noopener noreferrer" : undefined}
                                className={cn(
                                    "px-3 py-2 text-sm font-medium transition-colors duration-200 flex items-center gap-1",
                                    isActive(item.href)
                                        ? "text-white"
                                        : "text-zinc-400 hover:text-white"
                                )}
                            >
                                {item.label}
                                {item.hasDropdown && (
                                    <ChevronDown className="h-3 w-3" />
                                )}
                                {item.external && !item.hasDropdown && (
                                    <ExternalLink className="h-3 w-3" />
                                )}
                            </Link>
                        ))}
                    </div>

                    {/* Desktop CTA Buttons */}
                    <div className="hidden lg:flex items-center gap-3">
                        <Link href="/login">
                            <Button
                                variant="ghost"
                                size="sm"
                                className="text-zinc-400 hover:text-white border border-white/10 hover:border-white/20"
                            >
                                Login
                            </Button>
                        </Link>
                        <Link href="/signup">
                            <Button
                                variant="cyan"
                                size="sm"
                                className="font-mono text-sm"
                            >
                                Book a Demo
                            </Button>
                        </Link>
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                        className="lg:hidden p-2 rounded text-zinc-400 hover:text-white hover:bg-white/5 transition-colors"
                        aria-label={isMobileMenuOpen ? "Close menu" : "Open menu"}
                        aria-expanded={isMobileMenuOpen}
                    >
                        {isMobileMenuOpen ? (
                            <X className="h-5 w-5" />
                        ) : (
                            <Menu className="h-5 w-5" />
                        )}
                    </button>
                </div>

                {/* Mobile Menu */}
                <AnimatePresence>
                    {isMobileMenuOpen && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: "auto" }}
                            exit={{ opacity: 0, height: 0 }}
                            transition={{ duration: 0.2 }}
                            className="lg:hidden border-t border-white/[0.05] bg-[#0a0a0f]"
                        >
                            <div className="py-4 space-y-1">
                                {navItems.map((item) => (
                                    <Link
                                        key={item.href}
                                        href={item.href}
                                        className={cn(
                                            "flex items-center px-4 py-3 text-sm font-medium transition-all",
                                            "hover:bg-white/5",
                                            isActive(item.href)
                                                ? "text-white"
                                                : "text-zinc-400"
                                        )}
                                    >
                                        {item.label}
                                    </Link>
                                ))}
                                <div className="pt-4 px-4 space-y-2">
                                    <Link href="/login" className="block">
                                        <Button variant="outline" className="w-full">
                                            Login
                                        </Button>
                                    </Link>
                                    <Link href="/signup" className="block">
                                        <Button variant="cyan" className="w-full">
                                            Book a Demo
                                        </Button>
                                    </Link>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </nav>
        </header>
    );
}
