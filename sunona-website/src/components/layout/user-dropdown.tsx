/**
 * User Profile Dropdown Component - Sunona Style
 * Shows user info, account actions, and logout
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    User,
    CreditCard,
    Phone,
    PhoneCall,
    Shield,
    LogOut,
    ChevronDown,
} from "lucide-react";

interface UserDropdownProps {
    user: {
        name: string;
        email: string;
        avatarUrl?: string;
    };
    ongoingCalls?: number;
}

export function UserDropdown({ user, ongoingCalls = 0 }: UserDropdownProps) {
    const router = useRouter();
    const [isOpen, setIsOpen] = React.useState(false);
    const dropdownRef = React.useRef<HTMLDivElement>(null);

    // Close dropdown when clicking outside
    React.useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleLogout = () => {
        // Clear auth state
        router.push("/login");
    };

    const initials = user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2);

    return (
        <div className="relative" ref={dropdownRef}>
            {/* Trigger Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
                {user.avatarUrl ? (
                    <img
                        src={user.avatarUrl}
                        alt={user.name}
                        className="w-8 h-8 rounded-full"
                    />
                ) : (
                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium">
                        {initials}
                    </div>
                )}
                <span className="text-sm text-gray-700 hidden md:block">{user.email}</span>
                <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute top-full right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-100 py-2 z-50">
                    {/* User Info */}
                    <div className="px-4 py-3 border-b border-gray-100">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-sm font-medium">
                                {initials}
                            </div>
                            <div>
                                <p className="font-medium text-gray-900">{user.name}</p>
                                <p className="text-xs text-gray-500">{user.email}</p>
                            </div>
                        </div>
                    </div>

                    {/* Menu Items */}
                    <div className="py-2">
                        <Link
                            href="/dashboard/billing"
                            onClick={() => setIsOpen(false)}
                            className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                            <CreditCard className="w-4 h-4 text-gray-400" />
                            Recharge account
                        </Link>

                        <button
                            onClick={() => setIsOpen(false)}
                            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                            <PhoneCall className="w-4 h-4 text-gray-400" />
                            <span>Account</span>
                            <span className="ml-auto text-xs text-gray-400">{ongoingCalls} ongoing calls</span>
                        </button>

                        <Link
                            href="/dashboard/verified-numbers"
                            onClick={() => setIsOpen(false)}
                            className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                        >
                            <Shield className="w-4 h-4 text-gray-400" />
                            Verified numbers
                        </Link>
                    </div>

                    {/* Logout */}
                    <div className="border-t border-gray-100 pt-2">
                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                        >
                            <LogOut className="w-4 h-4" />
                            Log out
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
