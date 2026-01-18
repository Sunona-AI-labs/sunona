/**
 * Footer Component
 * Industrial-style footer with dotted underlines and minimal design
 */
"use client";

import * as React from "react";
import Link from "next/link";
import {
    Zap,
    Github,
    Twitter,
    Linkedin,
    Mail,
} from "lucide-react";

interface FooterLink {
    label: string;
    href: string;
    external?: boolean;
}

interface FooterSection {
    title: string;
    links: FooterLink[];
}

const footerSections: FooterSection[] = [
    {
        title: "Product",
        links: [
            { label: "Features", href: "/features" },
            { label: "Integrations", href: "/integrations" },
            { label: "Pricing", href: "/pricing" },
            { label: "Use Cases", href: "/use-cases" },
        ],
    },
    {
        title: "Developers",
        links: [
            { label: "Documentation", href: "/docs" },
            { label: "API Reference", href: "/docs" },
            { label: "SDKs", href: "/docs" },
            { label: "Status", href: "#", external: true },
        ],
    },
    {
        title: "Company",
        links: [
            { label: "About", href: "/about" },
            { label: "Careers", href: "/careers", external: true },
            { label: "Contact", href: "/contact" },
            { label: "Blog", href: "/blog" },
        ],
    },
    {
        title: "Legal",
        links: [
            { label: "Privacy", href: "/privacy" },
            { label: "Terms", href: "/terms" },
            { label: "Security", href: "/security" },
        ],
    },
];

const socialLinks = [
    { label: "GitHub", href: "https://github.com/sunona-ai", icon: Github },
    { label: "Twitter", href: "https://twitter.com/sunona_ai", icon: Twitter },
    { label: "LinkedIn", href: "https://linkedin.com/company/sunona-ai", icon: Linkedin },
    { label: "Email", href: "mailto:hello@sunona.ai", icon: Mail },
];

export function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-black border-t border-white/[0.05]">
            {/* Main Footer */}
            <div className="container-custom py-12 md:py-16">
                <div className="grid grid-cols-2 md:grid-cols-6 gap-8 lg:gap-12">
                    {/* Brand Section */}
                    <div className="col-span-2">
                        <Link href="/" className="flex items-center gap-2.5 mb-4">
                            <div className="bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-md p-1.5">
                                <Zap className="h-4 w-4 text-black" />
                            </div>
                            <span className="text-lg font-bold text-white tracking-tight">Sunona</span>
                        </Link>
                        <p className="text-zinc-500 text-sm mb-6 max-w-xs">
                            Build, deploy, and scale voice AI agents in minutes.
                            Enterprise-grade platform with 40+ integrations.
                        </p>
                        {/* Social Links */}
                        <div className="flex items-center gap-2">
                            {socialLinks.map((social) => (
                                <a
                                    key={social.label}
                                    href={social.href}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="p-2 rounded-md text-zinc-500 hover:text-white hover:bg-white/5 transition-colors"
                                    aria-label={social.label}
                                >
                                    <social.icon className="h-4 w-4" />
                                </a>
                            ))}
                        </div>
                    </div>

                    {/* Footer Links */}
                    {footerSections.map((section) => (
                        <div key={section.title}>
                            <h3 className="text-white font-medium mb-4 text-sm tracking-wide">
                                {section.title}
                            </h3>
                            <ul className="space-y-3">
                                {section.links.map((link) => (
                                    <li key={link.label}>
                                        {link.external ? (
                                            <a
                                                href={link.href}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="text-zinc-500 text-sm hover:text-white hover:underline hover:decoration-dotted underline-offset-4 transition-colors"
                                            >
                                                {link.label}
                                            </a>
                                        ) : (
                                            <Link
                                                href={link.href}
                                                className="text-zinc-500 text-sm hover:text-white hover:underline hover:decoration-dotted underline-offset-4 transition-colors"
                                            >
                                                {link.label}
                                            </Link>
                                        )}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="border-t border-white/[0.05]">
                <div className="container-custom py-6">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        <p className="text-zinc-600 text-sm">
                            © {currentYear} Sunona AI. All rights reserved.
                        </p>
                        <p className="text-zinc-600 text-sm font-mono text-xs tracking-wide">
                            VOICE AI INFRASTRUCTURE
                        </p>
                    </div>
                </div>
            </div>
        </footer>
    );
}
