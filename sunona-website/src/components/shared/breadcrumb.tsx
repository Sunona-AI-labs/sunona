/**
 * Breadcrumb Navigation Component
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronRight, Home } from "lucide-react";
import { cn } from "@/lib/utils";

interface BreadcrumbItem {
    label: string;
    href: string;
}

interface BreadcrumbProps {
    items?: BreadcrumbItem[];
    className?: string;
}

// Helper to generate breadcrumbs from pathname
function generateBreadcrumbs(pathname: string): BreadcrumbItem[] {
    const segments = pathname.split("/").filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [];

    let currentPath = "";
    for (const segment of segments) {
        currentPath += `/${segment}`;

        // Format segment to readable label
        let label = segment
            .split("-")
            .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");

        // Special cases
        if (segment === "dashboard") label = "Dashboard";
        if (segment === "agents") label = "Agents";
        if (segment === "new") label = "Create New";

        // Skip dynamic segments (like [id])
        if (segment.startsWith("[") && segment.endsWith("]")) {
            label = "Details";
        }

        breadcrumbs.push({
            label,
            href: currentPath,
        });
    }

    return breadcrumbs;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
    const pathname = usePathname();
    const breadcrumbs = items || generateBreadcrumbs(pathname);

    if (breadcrumbs.length <= 1) {
        return null; // Don't show breadcrumbs for single-level pages
    }

    return (
        <nav
            aria-label="Breadcrumb"
            className={cn("flex items-center text-sm text-gray-400", className)}
        >
            <Link
                href="/dashboard"
                className="flex items-center hover:text-white transition-colors"
            >
                <Home className="h-4 w-4" />
            </Link>

            {breadcrumbs.map((item, index) => (
                <React.Fragment key={item.href}>
                    <ChevronRight className="h-4 w-4 mx-2 text-gray-600" />
                    {index === breadcrumbs.length - 1 ? (
                        <span className="text-white font-medium">{item.label}</span>
                    ) : (
                        <Link
                            href={item.href}
                            className="hover:text-white transition-colors"
                        >
                            {item.label}
                        </Link>
                    )}
                </React.Fragment>
            ))}
        </nav>
    );
}
