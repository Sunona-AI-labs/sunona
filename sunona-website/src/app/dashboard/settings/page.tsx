/**
 * Settings Page - Clean Startup Style
 * Profile, team, and account settings
 */
"use client";

import * as React from "react";
import {
    User,
    Building2,
    Key,
    Shield,
    Bell,
    Save,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuthStore, selectUser } from "@/lib/store/auth-store";

export default function SettingsPage() {
    const user = useAuthStore(selectUser);
    const [activeTab, setActiveTab] = React.useState<"profile" | "organization" | "security" | "notifications">("profile");

    const [name, setName] = React.useState(user?.name || "");
    const [email, setEmail] = React.useState(user?.email || "");
    const [isSaving, setIsSaving] = React.useState(false);

    const handleSave = async () => {
        setIsSaving(true);
        // TODO: Save to backend
        await new Promise(resolve => setTimeout(resolve, 1000));
        setIsSaving(false);
    };

    return (
        <div className="max-w-4xl">
            {/* Page Header */}
            <div className="mb-6">
                <h1 className="text-xl font-semibold text-gray-900">Settings</h1>
                <p className="text-sm text-gray-500 mt-1">
                    Manage your account and preferences
                </p>
            </div>

            <div className="flex gap-6">
                {/* Sidebar Tabs */}
                <div className="w-48 flex-shrink-0">
                    <nav className="space-y-1">
                        {[
                            { id: "profile", label: "Profile", icon: User },
                            { id: "organization", label: "Organization", icon: Building2 },
                            { id: "security", label: "Security", icon: Shield },
                            { id: "notifications", label: "Notifications", icon: Bell },
                        ].map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as any)}
                                className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${activeTab === tab.id
                                        ? "bg-blue-50 text-blue-600 font-medium"
                                        : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                                    }`}
                            >
                                <tab.icon className={`w-4 h-4 ${activeTab === tab.id ? "text-blue-600" : "text-gray-400"
                                    }`} />
                                {tab.label}
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Content */}
                <div className="flex-1">
                    {activeTab === "profile" && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base">Profile Information</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {/* Avatar */}
                                <div className="flex items-center gap-4">
                                    <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center">
                                        <span className="text-xl font-semibold text-white">
                                            {name?.charAt(0)?.toUpperCase() || "U"}
                                        </span>
                                    </div>
                                    <div>
                                        <Button variant="ghost" size="sm">
                                            Change Avatar
                                        </Button>
                                    </div>
                                </div>

                                {/* Name */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Full Name
                                    </label>
                                    <input
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>

                                {/* Email */}
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Email Address
                                    </label>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>

                                {/* Save Button */}
                                <div className="pt-4">
                                    <Button onClick={handleSave} disabled={isSaving}>
                                        <Save className="w-4 h-4 mr-2" />
                                        {isSaving ? "Saving..." : "Save Changes"}
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {activeTab === "organization" && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base">Organization Settings</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Organization Name
                                    </label>
                                    <input
                                        type="text"
                                        defaultValue="My Organization"
                                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">
                                        Account ID
                                    </label>
                                    <input
                                        type="text"
                                        value={user?.accountId || "acc_..."}
                                        disabled
                                        className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-500"
                                    />
                                    <p className="text-xs text-gray-400 mt-1">
                                        This is your unique account identifier
                                    </p>
                                </div>

                                <div className="pt-4">
                                    <Button>
                                        <Save className="w-4 h-4 mr-2" />
                                        Save Changes
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {activeTab === "security" && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base">Security Settings</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                {/* Change Password */}
                                <div>
                                    <h4 className="text-sm font-medium text-gray-900 mb-3">Change Password</h4>
                                    <div className="space-y-3">
                                        <input
                                            type="password"
                                            placeholder="Current password"
                                            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                        <input
                                            type="password"
                                            placeholder="New password"
                                            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                        <input
                                            type="password"
                                            placeholder="Confirm new password"
                                            className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        />
                                    </div>
                                    <Button className="mt-3">Update Password</Button>
                                </div>

                                {/* Two-Factor */}
                                <div className="pt-4 border-t border-gray-200">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="text-sm font-medium text-gray-900">Two-Factor Authentication</h4>
                                            <p className="text-xs text-gray-500 mt-1">
                                                Add an extra layer of security to your account
                                            </p>
                                        </div>
                                        <Button variant="ghost" size="sm">
                                            Enable
                                        </Button>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>
                    )}

                    {activeTab === "notifications" && (
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-base">Notification Preferences</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {[
                                    { id: "email_calls", label: "Call notifications", description: "Get notified when calls complete" },
                                    { id: "email_billing", label: "Billing alerts", description: "Low balance and payment alerts" },
                                    { id: "email_updates", label: "Product updates", description: "New features and announcements" },
                                ].map((pref) => (
                                    <div key={pref.id} className="flex items-center justify-between py-2">
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">{pref.label}</p>
                                            <p className="text-xs text-gray-500">{pref.description}</p>
                                        </div>
                                        <label className="relative inline-flex items-center cursor-pointer">
                                            <input type="checkbox" defaultChecked className="sr-only peer" />
                                            <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                                        </label>
                                    </div>
                                ))}
                            </CardContent>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
