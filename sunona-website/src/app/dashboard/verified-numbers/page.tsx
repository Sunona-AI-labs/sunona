/**
 * Verified Phone Numbers Page - Sunona Style
 * Trial feature for verifying phone numbers
 */
"use client";

import * as React from "react";
import {
    Phone,
    Plus,
    Trash2,
    CheckCircle,
    Clock,
    XCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface VerifiedNumber {
    id: string;
    phoneNumber: string;
    status: "verified" | "pending" | "failed";
    createdAt: string;
}

export default function VerifiedNumbersPage() {
    const [numbers, setNumbers] = React.useState<VerifiedNumber[]>([]);
    const [showVerifyModal, setShowVerifyModal] = React.useState(false);

    const removeNumber = (id: string) => {
        setNumbers(numbers.filter((n) => n.id !== id));
    };

    const statusIcon = (status: VerifiedNumber["status"]) => {
        switch (status) {
            case "verified":
                return <CheckCircle className="w-4 h-4 text-green-500" />;
            case "pending":
                return <Clock className="w-4 h-4 text-amber-500" />;
            case "failed":
                return <XCircle className="w-4 h-4 text-red-500" />;
        }
    };

    return (
        <div className="max-w-4xl">
            {/* Trial Banner */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-2 mb-6 text-sm text-amber-800">
                You're currently on a trial plan, which limits outbound calls to your{" "}
                <a href="#" className="text-blue-600 underline">verified phone numbers</a>.
                To unlock full calling access, please upgrade by{" "}
                <a href="/dashboard/billing" className="text-blue-600 underline">adding funds to your account</a>.
            </div>

            {/* Page Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-xl font-semibold text-gray-900">My verified phone numbers</h1>
                    <p className="text-sm text-gray-500 mt-1">
                        Phone numbers to which calls can be made while the account is in trial.
                    </p>
                </div>
                <Button onClick={() => setShowVerifyModal(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    Verify phone number
                </Button>
            </div>

            {/* Phone Numbers Table */}
            <Card>
                <CardContent className="p-0">
                    {/* Table Header */}
                    <div className="grid grid-cols-4 gap-4 px-4 py-3 bg-gray-50 border-b border-gray-200 text-xs font-medium text-gray-500">
                        <div>Phone Number</div>
                        <div>Status</div>
                        <div>Created</div>
                        <div>Remove Phone number</div>
                    </div>

                    {/* Table Body */}
                    {numbers.length > 0 ? (
                        <div className="divide-y divide-gray-100">
                            {numbers.map((number) => (
                                <div
                                    key={number.id}
                                    className="grid grid-cols-4 gap-4 px-4 py-3 items-center text-sm"
                                >
                                    <div className="font-medium text-gray-900">{number.phoneNumber}</div>
                                    <div className="flex items-center gap-2">
                                        {statusIcon(number.status)}
                                        <span className="capitalize">{number.status}</span>
                                    </div>
                                    <div className="text-gray-500">{number.createdAt}</div>
                                    <div>
                                        <button
                                            onClick={() => removeNumber(number.id)}
                                            className="text-gray-400 hover:text-red-500 transition-colors"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-16">
                            <Phone className="w-12 h-12 mx-auto mb-4 text-gray-200" />
                            <p className="text-sm text-gray-500">No verified phone numbers added yet.</p>
                            <p className="text-xs text-gray-400 mt-1">
                                Add a phone number to start making calls during trial
                            </p>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Verify Modal */}
            {showVerifyModal && (
                <VerifyPhoneModal
                    onClose={() => setShowVerifyModal(false)}
                    onVerify={(phone) => {
                        setNumbers([
                            ...numbers,
                            {
                                id: crypto.randomUUID(),
                                phoneNumber: phone,
                                status: "pending",
                                createdAt: new Date().toLocaleDateString(),
                            },
                        ]);
                        setShowVerifyModal(false);
                    }}
                />
            )}
        </div>
    );
}

function VerifyPhoneModal({
    onClose,
    onVerify,
}: {
    onClose: () => void;
    onVerify: (phone: string) => void;
}) {
    const [phone, setPhone] = React.useState("");
    const [step, setStep] = React.useState<"phone" | "code">("phone");
    const [code, setCode] = React.useState("");
    const [isLoading, setIsLoading] = React.useState(false);

    const sendCode = async () => {
        setIsLoading(true);
        await new Promise((r) => setTimeout(r, 1000));
        setIsLoading(false);
        setStep("code");
    };

    const verifyCode = async () => {
        setIsLoading(true);
        await new Promise((r) => setTimeout(r, 1000));
        onVerify(phone);
    };

    return (
        <>
            <div className="fixed inset-0 bg-black/50 z-50" onClick={onClose} />
            <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-white rounded-xl shadow-xl z-50 p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-2">Verify Phone Number</h2>
                <p className="text-sm text-gray-500 mb-4">
                    {step === "phone"
                        ? "Enter your phone number to receive a verification code"
                        : "Enter the 6-digit code we sent to your phone"}
                </p>

                {step === "phone" ? (
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Phone Number</label>
                            <input
                                type="tel"
                                value={phone}
                                onChange={(e) => setPhone(e.target.value)}
                                placeholder="+1 (555) 123-4567"
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                            />
                        </div>

                        <div className="flex justify-end gap-3">
                            <Button variant="ghost" onClick={onClose}>Cancel</Button>
                            <Button disabled={!phone || isLoading} onClick={sendCode}>
                                {isLoading ? "Sending..." : "Send Code"}
                            </Button>
                        </div>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Verification Code</label>
                            <input
                                type="text"
                                value={code}
                                onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                                placeholder="000000"
                                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm font-mono text-center text-2xl tracking-widest"
                                maxLength={6}
                            />
                        </div>

                        <div className="flex justify-end gap-3">
                            <Button variant="ghost" onClick={() => setStep("phone")}>Back</Button>
                            <Button disabled={code.length !== 6 || isLoading} onClick={verifyCode}>
                                {isLoading ? "Verifying..." : "Verify"}
                            </Button>
                        </div>
                    </div>
                )}
            </div>
        </>
    );
}
