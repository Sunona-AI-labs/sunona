/**
 * Team Management Page
 * Manage team members and invitations
 */
"use client";

import * as React from "react";
import { motion } from "framer-motion";
import {
    Users,
    UserPlus,
    Mail,
    Shield,
    MoreVertical,
    Trash2,
    Edit,
    X,
    Check,
    Clock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar } from "@/components/ui/avatar";

// Mock team data
const mockMembers = [
    {
        id: "usr_001",
        name: "John Doe",
        email: "john@company.com",
        role: "admin",
        status: "active",
        joinedAt: "2025-12-01",
    },
    {
        id: "usr_002",
        name: "Jane Smith",
        email: "jane@company.com",
        role: "member",
        status: "active",
        joinedAt: "2025-12-10",
    },
    {
        id: "usr_003",
        name: "Bob Wilson",
        email: "bob@company.com",
        role: "viewer",
        status: "active",
        joinedAt: "2025-12-15",
    },
];

const mockInvites = [
    {
        id: "inv_001",
        email: "alice@company.com",
        role: "member",
        sentAt: "2 days ago",
    },
];

const roles = [
    { id: "admin", label: "Admin", description: "Full access to all features" },
    { id: "member", label: "Member", description: "Can create and manage agents" },
    { id: "viewer", label: "Viewer", description: "Read-only access" },
];

export default function TeamPage() {
    const [showInviteModal, setShowInviteModal] = React.useState(false);
    const [inviteEmail, setInviteEmail] = React.useState("");
    const [inviteRole, setInviteRole] = React.useState("member");

    const getRoleBadge = (role: string) => {
        switch (role) {
            case "admin":
                return <Badge variant="purple">Admin</Badge>;
            case "member":
                return <Badge variant="success">Member</Badge>;
            case "viewer":
                return <Badge variant="outline">Viewer</Badge>;
            default:
                return <Badge variant="outline">{role}</Badge>;
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-white">Team</h1>
                    <p className="text-gray-400 mt-1">
                        Manage your team members and permissions
                    </p>
                </div>
                <Button
                    leftIcon={<UserPlus className="h-4 w-4" />}
                    onClick={() => setShowInviteModal(true)}
                >
                    Invite Member
                </Button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <Card variant="bordered" className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-purple-500/10">
                            <Users className="h-5 w-5 text-purple-400" />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-white">{mockMembers.length}</div>
                            <div className="text-sm text-gray-400">Team Members</div>
                        </div>
                    </div>
                </Card>
                <Card variant="bordered" className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-amber-500/10">
                            <Clock className="h-5 w-5 text-amber-400" />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-white">{mockInvites.length}</div>
                            <div className="text-sm text-gray-400">Pending Invites</div>
                        </div>
                    </div>
                </Card>
                <Card variant="bordered" className="p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-emerald-500/10">
                            <Shield className="h-5 w-5 text-emerald-400" />
                        </div>
                        <div>
                            <div className="text-2xl font-bold text-white">
                                {mockMembers.filter((m) => m.role === "admin").length}
                            </div>
                            <div className="text-sm text-gray-400">Admins</div>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Team Members */}
            <Card variant="default">
                <CardHeader>
                    <CardTitle>Team Members</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {mockMembers.map((member) => (
                            <div
                                key={member.id}
                                className="flex items-center justify-between p-4 rounded-lg bg-[#1A1A2E]"
                            >
                                <div className="flex items-center gap-4">
                                    <Avatar fallback={member.name} size="md" />
                                    <div>
                                        <p className="text-white font-medium">{member.name}</p>
                                        <p className="text-sm text-gray-500">{member.email}</p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-4">
                                    {getRoleBadge(member.role)}
                                    <span className="text-sm text-gray-500">
                                        Joined {member.joinedAt}
                                    </span>
                                    <button className="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-[#252540] transition-colors">
                                        <MoreVertical className="h-4 w-4" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Pending Invites */}
            {mockInvites.length > 0 && (
                <Card variant="default">
                    <CardHeader>
                        <CardTitle>Pending Invitations</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            {mockInvites.map((invite) => (
                                <div
                                    key={invite.id}
                                    className="flex items-center justify-between p-4 rounded-lg bg-[#1A1A2E]"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className="p-2 rounded-full bg-amber-500/10">
                                            <Mail className="h-5 w-5 text-amber-400" />
                                        </div>
                                        <div>
                                            <p className="text-white font-medium">{invite.email}</p>
                                            <p className="text-sm text-gray-500">Sent {invite.sentAt}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        {getRoleBadge(invite.role)}
                                        <Button variant="ghost" size="sm">
                                            Resend
                                        </Button>
                                        <button className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors">
                                            <Trash2 className="h-4 w-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Invite Modal */}
            {showInviteModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="w-full max-w-md"
                    >
                        <Card variant="elevated">
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle>Invite Team Member</CardTitle>
                                <button
                                    onClick={() => setShowInviteModal(false)}
                                    className="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-[#252540] transition-colors"
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <Input
                                    label="Email Address"
                                    type="email"
                                    placeholder="colleague@company.com"
                                    value={inviteEmail}
                                    onChange={(e) => setInviteEmail(e.target.value)}
                                    leftIcon={<Mail className="h-4 w-4" />}
                                />

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Role
                                    </label>
                                    <div className="space-y-2">
                                        {roles.map((role) => (
                                            <button
                                                key={role.id}
                                                onClick={() => setInviteRole(role.id)}
                                                className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${inviteRole === role.id
                                                        ? "bg-purple-500/10 border border-purple-500/50"
                                                        : "bg-[#1A1A2E] border border-transparent hover:border-[#374151]"
                                                    }`}
                                            >
                                                <div className="text-left">
                                                    <p className="text-white font-medium">{role.label}</p>
                                                    <p className="text-xs text-gray-500">{role.description}</p>
                                                </div>
                                                {inviteRole === role.id && (
                                                    <Check className="h-5 w-5 text-purple-400" />
                                                )}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <Button
                                    className="w-full"
                                    disabled={!inviteEmail}
                                    leftIcon={<Mail className="h-4 w-4" />}
                                >
                                    Send Invitation
                                </Button>
                            </CardContent>
                        </Card>
                    </motion.div>
                </div>
            )}
        </div>
    );
}
