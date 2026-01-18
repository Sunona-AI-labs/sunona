/**
 * Card Component
 * Industrial-style card with sharp corners and subtle borders
 */
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: "default" | "elevated" | "bordered" | "glass" | "glow";
    hover?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
    ({ className, variant = "default", hover = false, ...props }, ref) => {
        const variants = {
            default: "bg-zinc-900/40 border-white/[0.05]",
            elevated: "bg-zinc-900/60 border-white/[0.08] shadow-2xl",
            bordered: "bg-transparent border-white/[0.08]",
            glass: cn(
                "bg-black/40 backdrop-blur-md",
                "border-white/[0.05]"
            ),
            glow: "bg-zinc-900/60 border-purple-500/20 shadow-[0_0_40px_rgba(168,85,247,0.05)] hover:border-purple-500/40 hover:shadow-[0_0_50px_rgba(168,85,247,0.1)]",
        };

        return (
            <div
                ref={ref}
                className={cn(
                    "rounded-xl border transition-all duration-500 ease-out",
                    variants[variant],
                    hover && "hover:-translate-y-1 hover:border-white/20 hover:bg-zinc-900/80 cursor-pointer shadow-lg hover:shadow-2xl",
                    className
                )}
                {...props}
            />
        );
    }
);
Card.displayName = "Card";

const CardHeader = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn("flex flex-col space-y-1.5 p-6", className)}
        {...props}
    />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
    HTMLHeadingElement,
    React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
    <h3
        ref={ref}
        className={cn(
            "text-lg font-semibold leading-none tracking-tight text-white",
            className
        )}
        {...props}
    />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
    HTMLParagraphElement,
    React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
    <p
        ref={ref}
        className={cn("text-sm text-zinc-400 mt-1.5", className)}
        {...props}
    />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
    HTMLDivElement,
    React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
    <div
        ref={ref}
        className={cn("flex items-center p-6 pt-0", className)}
        {...props}
    />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
