/**
 * Avatar Component
 * User/agent avatars with fallback initials
 */
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
    src?: string | null;
    alt?: string;
    fallback?: string;
    size?: "xs" | "sm" | "md" | "lg" | "xl";
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
    ({ className, src, alt, fallback, size = "md", ...props }, ref) => {
        const [hasError, setHasError] = React.useState(false);

        const sizes = {
            xs: "h-6 w-6 text-xs",
            sm: "h-8 w-8 text-sm",
            md: "h-10 w-10 text-base",
            lg: "h-12 w-12 text-lg",
            xl: "h-16 w-16 text-xl",
        };

        // Generate initials from fallback text
        const initials = React.useMemo(() => {
            if (!fallback) return "?";
            const words = fallback.trim().split(" ");
            if (words.length === 1) {
                return words[0].substring(0, 2).toUpperCase();
            }
            return (words[0][0] + words[words.length - 1][0]).toUpperCase();
        }, [fallback]);

        // Generate consistent color from fallback text
        const bgColor = React.useMemo(() => {
            if (!fallback) return "bg-purple-600";
            const colors = [
                "bg-purple-600",
                "bg-blue-600",
                "bg-emerald-600",
                "bg-amber-600",
                "bg-rose-600",
                "bg-cyan-600",
                "bg-indigo-600",
            ];
            const index = fallback.charCodeAt(0) % colors.length;
            return colors[index];
        }, [fallback]);

        return (
            <div
                ref={ref}
                className={cn(
                    "relative inline-flex items-center justify-center rounded-full overflow-hidden",
                    "bg-[#252540] text-white font-medium",
                    sizes[size],
                    !src && bgColor,
                    className
                )}
                {...props}
            >
                {src && !hasError ? (
                    <img
                        src={src}
                        alt={alt || fallback || "Avatar"}
                        className="h-full w-full object-cover"
                        onError={() => setHasError(true)}
                    />
                ) : (
                    <span>{initials}</span>
                )}
            </div>
        );
    }
);

Avatar.displayName = "Avatar";

export { Avatar };
