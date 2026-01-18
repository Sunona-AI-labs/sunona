/**
 * Button Component
 * Supports both dark (marketing) and light (dashboard) themes
 */
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "outline" | "ghost" | "danger" | "success" | "cyan" | "subtle" | "link";
    size?: "sm" | "md" | "lg" | "icon";
    isLoading?: boolean;
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
    glow?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    (
        {
            className,
            variant = "primary",
            size = "md",
            isLoading = false,
            leftIcon,
            rightIcon,
            disabled,
            glow = false,
            children,
            ...props
        },
        ref
    ) => {
        const baseStyles = cn(
            "inline-flex items-center justify-center gap-2",
            "font-medium rounded-lg transition-all duration-300",
            "focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
            "focus-visible:ring-blue-500/50",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            "active:scale-[0.97]"
        );

        const variants = {
            primary: cn(
                "bg-blue-600 hover:bg-blue-500",
                "text-white shadow-[0_4px_14px_0_rgba(37,99,235,0.39)]",
                "hover:shadow-[0_6px_20px_rgba(37,99,235,0.23)]",
                "border border-blue-500/10"
            ),
            secondary: cn(
                "bg-white/10 hover:bg-white/15",
                "text-white border border-white/10",
                "backdrop-blur-sm"
            ),
            outline: cn(
                "bg-transparent border border-white/20",
                "text-gray-300 hover:text-white hover:border-white/40",
                "hover:bg-white/5"
            ),
            ghost: cn(
                "bg-transparent",
                "text-gray-400 hover:text-white",
                "hover:bg-white/5"
            ),
            danger: cn(
                "bg-red-500/10 hover:bg-red-500/20",
                "text-red-400 border border-red-500/20"
            ),
            success: cn(
                "bg-emerald-500/10 hover:bg-emerald-500/20",
                "text-emerald-400 border border-emerald-500/20"
            ),
            cyan: cn(
                "bg-cyan-500 text-black font-bold",
                "hover:bg-cyan-400 shadow-[0_0_20px_rgba(34,211,238,0.3)]",
                "hover:shadow-[0_0_30px_rgba(34,211,238,0.5)]"
            ),
            subtle: cn(
                "bg-blue-500/5 hover:bg-blue-500/10",
                "text-blue-400 border border-blue-500/10"
            ),
            link: cn(
                "bg-transparent underline-offset-4 hover:underline",
                "text-blue-400 hover:text-blue-300 p-0 h-auto"
            ),
        };

        const sizes = {
            sm: "h-8 px-3 text-xs",
            md: "h-10 px-4 text-sm",
            lg: "h-12 px-6 text-base",
            icon: "h-10 w-10 p-0",
        };

        const glowStyles = glow ? cn(
            "relative overflow-hidden",
            "after:absolute after:inset-0 after:bg-gradient-to-r after:from-transparent after:via-white/10 after:to-transparent",
            "after:translate-x-[-200%] hover:after:translate-x-[200%] after:transition-transform after:duration-[1.5s]",
            "shadow-[0_0_30px_rgba(37,99,235,0.2)]"
        ) : "";

        return (
            <button
                className={cn(baseStyles, variants[variant], sizes[size], glowStyles, className)}
                ref={ref}
                disabled={disabled || isLoading}
                {...props}
            >
                {isLoading ? (
                    <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        {size !== "icon" && <span>Processing...</span>}
                    </div>
                ) : (
                    <>
                        {leftIcon && <span className="inline-flex shrink-0">{leftIcon}</span>}
                        <span>{children}</span>
                        {rightIcon && <span className="inline-flex shrink-0">{rightIcon}</span>}
                    </>
                )}
            </button>
        );
    }
);

Button.displayName = "Button";

export { Button };
