/**
 * Dashboard Home Page - Stats Overview
 * Shows key metrics and recent activity
 */
"use client";

import * as React from "react";
import Link from "next/link";
import {
    PhoneCall,
    Bot,
    Clock,
    DollarSign,
    TrendingUp,
    TrendingDown,
    ArrowRight,
    Play,
    Pause,
} from "lucide-react";
import { cn } from "@/lib/utils";

// Stats data for Sunona (costs based on $0.04/min rate)
const statsData = [
    {
        title: "Total Calls",
        value: "2,847",
        change: "+12%",
        trend: "up",
        icon: PhoneCall,
        color: "blue",
        description: "from last month",
    },
    {
        title: "Active Agents",
        value: "12",
        change: "+3",
        trend: "up",
        icon: Bot,
        color: "green",
        description: "new this week",
    },
    {
        title: "Minutes Used",
        value: "4,521",
        change: "+8%",
        trend: "up",
        icon: Clock,
        color: "purple",
        description: "from last month",
    },
    {
        title: "Total Spent",
        value: "$180.84", // 4,521 mins × $0.04 = $180.84
        change: "-15%",
        trend: "down",
        icon: DollarSign,
        color: "amber",
        description: "saved this month",
    },
];

// Recent activity data (costs based on $0.04/min rate)
const recentActivity = [
    { id: "call_001", agent: "Customer Support", user: "+91812345678", duration: "2:45", status: "completed", cost: "$0.11", time: "2 min ago" },
    { id: "call_002", agent: "Sales Outreach", user: "+91987654321", duration: "5:12", status: "completed", cost: "$0.21", time: "5 min ago" },
    { id: "call_003", agent: "Recruiter AI", user: "+91765432100", duration: "1:30", status: "no-answer", cost: "$0.06", time: "12 min ago" },
    { id: "call_004", agent: "Customer Support", user: "+91654321098", duration: "3:22", status: "completed", cost: "$0.13", time: "18 min ago" },
    { id: "call_005", agent: "Welcome Agent", user: "+91543210987", duration: "4:05", status: "completed", cost: "$0.16", time: "25 min ago" },
];

// Quick actions
const quickActions = [
    { label: "Create Agent", href: "/dashboard/agents", icon: Bot },
    { label: "View Calls", href: "/dashboard/calls", icon: PhoneCall },
    { label: "Upload Knowledge", href: "/dashboard/knowledge", icon: DollarSign },
];

export default function DashboardPage() {
    return (
        <div className="space-y-6">
            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {statsData.map((stat, index) => (
                    <div
                        key={index}
                        className="p-6 bg-white rounded-xl border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <div className={cn(
                                "p-2.5 rounded-lg",
                                stat.color === "blue" && "bg-blue-100",
                                stat.color === "green" && "bg-green-100",
                                stat.color === "purple" && "bg-purple-100",
                                stat.color === "amber" && "bg-amber-100",
                            )}>
                                <stat.icon className={cn(
                                    "w-5 h-5",
                                    stat.color === "blue" && "text-blue-600",
                                    stat.color === "green" && "text-green-600",
                                    stat.color === "purple" && "text-purple-600",
                                    stat.color === "amber" && "text-amber-600",
                                )} />
                            </div>
                            <div className={cn(
                                "flex items-center gap-1 text-xs font-medium",
                                stat.trend === "up" ? "text-green-600" : "text-red-500"
                            )}>
                                {stat.trend === "up" ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                                {stat.change}
                            </div>
                        </div>
                        <p className="text-2xl font-bold text-gray-900 mb-1">
                            {stat.value}
                        </p>
                        <p className="text-sm text-gray-500">
                            {stat.title}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                            {stat.description}
                        </p>
                    </div>
                ))}
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                    <div>
                        <h2 className="text-lg font-semibold text-gray-900">
                            Recent Activity
                        </h2>
                        <p className="text-sm text-gray-500">
                            Your latest call activity
                        </p>
                    </div>
                    <Link
                        href="/dashboard/calls"
                        className="text-sm text-blue-500 hover:text-blue-600 font-medium flex items-center gap-1"
                    >
                        View all
                        <ArrowRight size={14} />
                    </Link>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead>
                            <tr className="bg-gray-50">
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Call ID
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Agent
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    User
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Duration
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Status
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Cost
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Time
                                </th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                    Actions
                                </th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                            {recentActivity.map((activity) => (
                                <tr key={activity.id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 text-sm font-mono text-gray-900">
                                        {activity.id}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-900">
                                        {activity.agent}
                                    </td>
                                    <td className="px-6 py-4 text-sm font-mono text-gray-500">
                                        {activity.user}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-900">
                                        {activity.duration}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={cn(
                                            "px-2.5 py-1 text-xs font-medium rounded-full",
                                            activity.status === "completed"
                                                ? "bg-green-100 text-green-700"
                                                : "bg-red-100 text-red-700"
                                        )}>
                                            {activity.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-sm font-medium text-gray-900">
                                        {activity.cost}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        {activity.time}
                                    </td>
                                    <td className="px-6 py-4">
                                        <button className="p-1.5 rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors">
                                            <Play size={14} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {quickActions.map((action, index) => (
                    <Link
                        key={index}
                        href={action.href}
                        className="p-4 bg-white rounded-xl border border-gray-200 hover:border-blue-200 hover:shadow-md transition-all flex items-center gap-4 group"
                    >
                        <div className="p-3 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                            <action.icon className="w-5 h-5 text-blue-600" />
                        </div>
                        <div className="flex-1">
                            <p className="font-medium text-gray-900">{action.label}</p>
                            <p className="text-sm text-gray-500">Get started quickly</p>
                        </div>
                        <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-blue-500 transition-colors" />
                    </Link>
                ))}
            </div>
        </div>
    );
}
