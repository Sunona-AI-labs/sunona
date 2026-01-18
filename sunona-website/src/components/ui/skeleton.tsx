/**
 * Skeleton Loading Components
 * Placeholder animations for loading states
 */
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: "text" | "circular" | "rectangular" | "card";
    width?: string | number;
    height?: string | number;
    animate?: boolean;
}

export function Skeleton({
    className,
    variant = "rectangular",
    width,
    height,
    animate = true,
    ...props
}: SkeletonProps) {
    const baseStyles = cn(
        "bg-gradient-to-r from-[#1A1A2E] via-[#252540] to-[#1A1A2E]",
        animate && "animate-pulse bg-[length:200%_100%]",
        variant === "circular" && "rounded-full",
        variant === "text" && "rounded h-4",
        variant === "rectangular" && "rounded-lg",
        variant === "card" && "rounded-xl",
        className
    );

    return (
        <div
            className={baseStyles}
            style={{
                width: width,
                height: height,
            }}
            {...props}
        />
    );
}

// Pre-built skeleton patterns
export function SkeletonCard() {
    return (
        <div className="p-6 rounded-xl bg-[#1A1A2E] border border-[#374151] space-y-4">
            <div className="flex items-center gap-4">
                <Skeleton variant="circular" width={40} height={40} />
                <div className="space-y-2 flex-1">
                    <Skeleton variant="text" width="60%" />
                    <Skeleton variant="text" width="40%" />
                </div>
            </div>
            <Skeleton variant="rectangular" height={80} />
            <div className="flex gap-2">
                <Skeleton variant="rectangular" width={80} height={32} />
                <Skeleton variant="rectangular" width={80} height={32} />
            </div>
        </div>
    );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
    return (
        <div className="space-y-3">
            {/* Header */}
            <div className="flex gap-4 p-4 border-b border-[#374151]">
                <Skeleton variant="text" width="20%" />
                <Skeleton variant="text" width="25%" />
                <Skeleton variant="text" width="15%" />
                <Skeleton variant="text" width="20%" />
                <Skeleton variant="text" width="20%" />
            </div>
            {/* Rows */}
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex gap-4 p-4 items-center">
                    <div className="flex items-center gap-3 w-[20%]">
                        <Skeleton variant="circular" width={32} height={32} />
                        <Skeleton variant="text" className="flex-1" />
                    </div>
                    <Skeleton variant="text" width="25%" />
                    <Skeleton variant="text" width="15%" />
                    <Skeleton variant="text" width="20%" />
                    <Skeleton variant="rectangular" width={60} height={24} />
                </div>
            ))}
        </div>
    );
}

export function SkeletonStats() {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="p-6 rounded-xl bg-[#1A1A2E] border border-[#374151]">
                    <div className="flex items-center justify-between mb-4">
                        <Skeleton variant="rectangular" width={40} height={40} />
                        <Skeleton variant="text" width={60} />
                    </div>
                    <Skeleton variant="text" width="50%" height={28} className="mb-2" />
                    <Skeleton variant="text" width="70%" />
                </div>
            ))}
        </div>
    );
}

export function SkeletonAgentCard() {
    return (
        <div className="p-6 rounded-xl bg-[#1A1A2E] border border-[#374151] space-y-4">
            <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                    <Skeleton variant="circular" width={40} height={40} />
                    <div className="space-y-2">
                        <Skeleton variant="text" width={120} />
                        <Skeleton variant="text" width={80} />
                    </div>
                </div>
                <Skeleton variant="rectangular" width={70} height={24} />
            </div>
            <Skeleton variant="text" width="100%" />
            <Skeleton variant="text" width="80%" />
            <div className="flex gap-2">
                <Skeleton variant="rectangular" width={80} height={24} />
                <Skeleton variant="rectangular" width={80} height={24} />
                <Skeleton variant="rectangular" width={80} height={24} />
            </div>
            <div className="flex gap-2 pt-4 border-t border-[#374151]">
                <Skeleton variant="rectangular" className="flex-1" height={36} />
                <Skeleton variant="rectangular" width={80} height={36} />
                <Skeleton variant="rectangular" width={40} height={36} />
            </div>
        </div>
    );
}
