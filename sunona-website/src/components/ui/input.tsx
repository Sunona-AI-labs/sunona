/**
 * Input Component
 * Industrial-style input with sharp corners and subtle borders
 */
"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
    hint?: string;
    leftIcon?: React.ReactNode;
    rightIcon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
    ({ className, type, label, error, hint, leftIcon, rightIcon, id, ...props }, ref) => {
        const inputId = id || React.useId();

        return (
            <div className="w-full">
                {label && (
                    <label
                        htmlFor={inputId}
                        className="block text-sm font-medium text-zinc-400 mb-2"
                    >
                        {label}
                    </label>
                )}
                <div className="relative group">
                    {leftIcon && (
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-zinc-500 group-focus-within:text-cyan-500 transition-colors">
                            {leftIcon}
                        </div>
                    )}
                    <input
                        type={type}
                        id={inputId}
                        className={cn(
                            "flex h-11 w-full rounded-lg border bg-zinc-900/50 px-3 py-2",
                            "text-white text-sm placeholder:text-zinc-600",
                            "border-white/10 focus:border-cyan-500/50",
                            "focus:outline-none focus:ring-4 focus:ring-cyan-500/10",
                            "transition-all duration-300",
                            "disabled:cursor-not-allowed disabled:opacity-50",
                            leftIcon && "pl-10",
                            rightIcon && "pr-10",
                            error && "border-red-500/50 focus:border-red-500 focus:ring-red-500/10",
                            className
                        )}
                        ref={ref}
                        aria-invalid={!!error}
                        aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
                        {...props}
                    />
                    {rightIcon && (
                        <div className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-500 group-focus-within:text-cyan-500 transition-colors">
                            {rightIcon}
                        </div>
                    )}
                </div>
                {error && (
                    <p id={`${inputId}-error`} className="mt-2 text-xs text-red-400 font-medium flex items-center gap-1">
                        <span className="w-1 h-1 rounded-full bg-red-400" />
                        {error}
                    </p>
                )}
                {hint && !error && (
                    <p id={`${inputId}-hint`} className="mt-2 text-xs text-zinc-500 font-medium">
                        {hint}
                    </p>
                )}
            </div>
        );
    }
);

Input.displayName = "Input";

export { Input };
