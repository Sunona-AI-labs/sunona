/**
 * Analytics Dashboard Page
 * Charts and metrics for call performance
 */
"use client";

import * as React from "react";
import { motion } from "framer-motion";
import {
    BarChart3,
    TrendingUp,
    TrendingDown,
    Phone,
    Clock,
    DollarSign,
    Users,
    Calendar,
    Download,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// Mock data
const statsCards = [
    {
        title: "Total Calls",
        value: "12,847",
        change: "+12.5%",
        trend: "up" as const,
        icon: Phone,
    },
    {
        title: "Avg Duration",
        value: "3:42",
        change: "+8.2%",
        trend: "up" as const,
        icon: Clock,
    },
    {
        title: "Total Cost",
        value: "$2,458.32",
        change: "+15.3%",
        trend: "up" as const,
        icon: DollarSign,
    },
    {
        title: "Success Rate",
        value: "94.2%",
        change: "+2.1%",
        trend: "up" as const,
        icon: TrendingUp,
    },
];

const topAgents = [
    { name: "Sales Assistant", calls: 3420, successRate: 96.2, avgDuration: "4:12" },
    { name: "Support Bot", calls: 2890, successRate: 94.8, avgDuration: "3:45" },
    { name: "Lead Qualifier", calls: 2145, successRate: 92.1, avgDuration: "2:58" },
    { name: "Appointment Booker", calls: 1876, successRate: 95.4, avgDuration: "5:02" },
    { name: "Survey Collector", calls: 1234, successRate: 88.7, avgDuration: "1:45" },
];

const costBreakdown = [
    { category: "STT (Deepgram)", amount: 845.20, percentage: 34.4 },
    { category: "TTS (ElevenLabs)", amount: 623.50, percentage: 25.4 },
    { category: "LLM (GPT-4o)", amount: 512.30, percentage: 20.8 },
    { category: "Telephony (Twilio)", amount: 477.32, percentage: 19.4 },
];

const dailyCalls = [
    { day: "Mon", calls: 245, cost: 42.30 },
    { day: "Tue", calls: 312, cost: 54.20 },
    { day: "Wed", calls: 287, cost: 48.90 },
    { day: "Thu", calls: 356, cost: 61.20 },
    { day: "Fri", calls: 398, cost: 68.50 },
    { day: "Sat", calls: 156, cost: 26.80 },
    { day: "Sun", calls: 93, cost: 15.90 },
];

export default function AnalyticsPage() {
    const [timeRange, setTimeRange] = React.useState<"7d" | "30d" | "90d">("30d");

    const maxCalls = Math.max(...dailyCalls.map((d) => d.calls));

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">Analytics</h1>
                    <p className="text-gray-400 mt-1">
                        Track performance and usage metrics
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="flex items-center bg-[#1A1A2E] rounded-lg p-1">
                        {(["7d", "30d", "90d"] as const).map((range) => (
                            <button
                                key={range}
                                onClick={() => setTimeRange(range)}
                                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${timeRange === range
                                        ? "bg-purple-500 text-white"
                                        : "text-gray-400 hover:text-white"
                                    }`}
                            >
                                {range === "7d" ? "7 Days" : range === "30d" ? "30 Days" : "90 Days"}
                            </button>
                        ))}
                    </div>
                    <Button variant="outline" leftIcon={<Download className="h-4 w-4" />}>
                        Export
                    </Button>
                </div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {statsCards.map((stat, index) => (
                    <motion.div
                        key={stat.title}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                    >
                        <Card variant="default">
                            <CardContent className="p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="p-2 rounded-lg bg-purple-500/10">
                                        <stat.icon className="h-5 w-5 text-purple-400" />
                                    </div>
                                    <div
                                        className={`flex items-center gap-1 text-sm ${stat.trend === "up" ? "text-emerald-400" : "text-red-400"
                                            }`}
                                    >
                                        {stat.trend === "up" ? (
                                            <TrendingUp className="h-4 w-4" />
                                        ) : (
                                            <TrendingDown className="h-4 w-4" />
                                        )}
                                        {stat.change}
                                    </div>
                                </div>
                                <div className="text-2xl font-bold text-white">{stat.value}</div>
                                <div className="text-sm text-gray-400">{stat.title}</div>
                            </CardContent>
                        </Card>
                    </motion.div>
                ))}
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Daily Calls Chart */}
                <Card variant="default">
                    <CardHeader>
                        <CardTitle className="text-lg">Calls This Week</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-end justify-between h-48 gap-2">
                            {dailyCalls.map((day) => (
                                <div key={day.day} className="flex-1 flex flex-col items-center gap-2">
                                    <div
                                        className="w-full bg-purple-500/20 rounded-t-md transition-all hover:bg-purple-500/30"
                                        style={{
                                            height: `${(day.calls / maxCalls) * 100}%`,
                                            minHeight: "8px",
                                        }}
                                    >
                                        <div
                                            className="w-full bg-purple-500 rounded-t-md"
                                            style={{
                                                height: `${(day.calls / maxCalls) * 100}%`,
                                            }}
                                        />
                                    </div>
                                    <span className="text-xs text-gray-500">{day.day}</span>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>

                {/* Cost Breakdown */}
                <Card variant="default">
                    <CardHeader>
                        <CardTitle className="text-lg">Cost Breakdown</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            {costBreakdown.map((item, index) => (
                                <div key={item.category}>
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-sm text-gray-300">{item.category}</span>
                                        <span className="text-sm text-white font-medium">
                                            ${item.amount.toFixed(2)}
                                        </span>
                                    </div>
                                    <div className="h-2 bg-[#252540] rounded-full overflow-hidden">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${item.percentage}%` }}
                                            transition={{ duration: 0.5, delay: index * 0.1 }}
                                            className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full"
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Top Agents Table */}
            <Card variant="default">
                <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle className="text-lg">Top Performing Agents</CardTitle>
                    <Badge variant="outline">Last {timeRange}</Badge>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-[#374151]">
                                    <th className="text-left text-sm font-medium text-gray-400 pb-3">Agent</th>
                                    <th className="text-right text-sm font-medium text-gray-400 pb-3">Calls</th>
                                    <th className="text-right text-sm font-medium text-gray-400 pb-3">Success Rate</th>
                                    <th className="text-right text-sm font-medium text-gray-400 pb-3">Avg Duration</th>
                                </tr>
                            </thead>
                            <tbody>
                                {topAgents.map((agent, index) => (
                                    <tr key={agent.name} className="border-b border-[#374151]/50">
                                        <td className="py-3">
                                            <div className="flex items-center gap-3">
                                                <span className="w-6 h-6 rounded-full bg-purple-500/20 text-purple-400 text-xs flex items-center justify-center font-medium">
                                                    {index + 1}
                                                </span>
                                                <span className="text-white font-medium">{agent.name}</span>
                                            </div>
                                        </td>
                                        <td className="py-3 text-right text-gray-300">
                                            {agent.calls.toLocaleString()}
                                        </td>
                                        <td className="py-3 text-right">
                                            <Badge
                                                variant={agent.successRate >= 95 ? "success" : agent.successRate >= 90 ? "warning" : "error"}
                                                size="sm"
                                            >
                                                {agent.successRate}%
                                            </Badge>
                                        </td>
                                        <td className="py-3 text-right text-gray-300">{agent.avgDuration}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
