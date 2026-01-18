/**
 * Reusable Search Input Component
 * Consistent styling and functionality across all dashboard pages
 */
"use client";

import * as React from "react";
import { Search, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchInputProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    className?: string;
    autoFocus?: boolean;
    onFocus?: () => void;
    onBlur?: () => void;
}

export function SearchInput({
    value,
    onChange,
    placeholder = "Search...",
    className,
    autoFocus = false,
    onFocus,
    onBlur,
}: SearchInputProps) {
    const inputRef = React.useRef<HTMLInputElement>(null);

    const handleClear = () => {
        onChange("");
        inputRef.current?.focus();
    };

    return (
        <div className={cn("relative", className)}>
            <div className="absolute inset-y-0 left-0 flex items-center pointer-events-none" style={{ paddingLeft: '14px' }}>
                <Search className="w-4 h-4 text-gray-400" />
            </div>
            <input
                ref={inputRef}
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                autoFocus={autoFocus}
                onFocus={onFocus}
                onBlur={onBlur}
                style={{ paddingLeft: '40px' }}
                className={cn(
                    "w-full pr-9 py-2.5 text-sm rounded-xl border transition-all duration-200",
                    "bg-gray-50 border-gray-200 text-gray-900 placeholder:text-gray-400",
                    "hover:border-gray-300 hover:bg-gray-100",
                    "focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 focus:bg-white",
                )}
            />
            {value && (
                <button
                    onClick={handleClear}
                    className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 rounded-full hover:bg-gray-200 transition-colors"
                >
                    <X className="w-3.5 h-3.5 text-gray-400" />
                </button>
            )}
        </div>
    );


}

export default SearchInput;
