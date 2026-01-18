/**
 * Badge Component
 * Status indicators and labels with industrial styling
 */
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
    variant?: "default" | "success" | "warning" | "error" | "info" | "purple" | "cyan" | "outline" | "mono" | "soft";
    size?: "sm" | "md" | "lg";
    dot?: boolean;
}

const Badge = React.forwardRef<HTMLSpanElement, BadgeProps>(
    ({ className, variant = "default", size = "md", dot = false, children, ...props }, ref) => {
        const variants = {
            default: "bg-white/5 text-gray-300 border border-white/10",
            success: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
            warning: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
            error: "bg-red-500/10 text-red-400 border border-red-500/20",
            info: "bg-blue-500/10 text-blue-400 border border-blue-500/20",
            purple: "bg-purple-500/10 text-purple-400 border border-purple-500/20",
            cyan: "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20",
            outline: "bg-transparent text-gray-400 border border-white/10",
            mono: "bg-black text-gray-400 font-mono uppercase tracking-[0.2em] text-[9px] px-2 py-0.5 border border-white/5",
            soft: "bg-blue-400/5 text-blue-400/70 border border-blue-400/10",
        };

        const sizes = {
            sm: "text-[10px] px-1.5 py-0.5",
            md: "text-[11px] px-2.5 py-1",
            lg: "text-xs px-3 py-1.5",
        };

        const dotColors = {
            default: "bg-gray-400",
            success: "bg-emerald-400",
            warning: "bg-amber-400",
            error: "bg-red-400",
            info: "bg-blue-400",
            purple: "bg-purple-400",
            cyan: "bg-cyan-400",
            outline: "bg-gray-400",
            mono: "bg-gray-500",
            soft: "bg-blue-400",
        };

        return (
            <span
                ref={ref}
                className={cn(
                    "inline-flex items-center gap-1.5 font-semibold transition-all duration-200",
                    variant === "mono" ? "rounded-sm" : "rounded-full",
                    variants[variant],
                    variant !== "mono" && sizes[size],
                    className
                )}
                {...props}
            >
                {dot && (
                    <span
                        className={cn(
                            "w-1 h-1 rounded-full shrink-0 shadow-[0_0_8px_currentColor]",
                            dotColors[variant],
                            "animate-pulse"
                        )}
                        style={{ animationDuration: '2s' }}
                    />
                )}
                <span className="leading-none">{children}</span>
            </span>
        );
    }
);

Badge.displayName = "Badge";

export { Badge };
