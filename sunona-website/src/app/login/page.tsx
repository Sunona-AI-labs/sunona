/**
 * Login Page - Sunona Dark Industrial AI Theme
 * Beautiful centered login with OAuth options
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Eye, EyeOff, ExternalLink, Mic2, MessageCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/store/auth-store";

export default function LoginPage() {
    const router = useRouter();
    const login = useAuthStore((state) => state.login);
    const [email, setEmail] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [showPassword, setShowPassword] = React.useState(false);
    const [isLoading, setIsLoading] = React.useState(false);

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        // Simulate API call
        await new Promise((r) => setTimeout(r, 500));

        // Create mock user and call auth store login
        const mockUser = {
            id: "user_demo_001",
            email: email || "demo@sunona.ai",
            name: "Demo User",
            accountId: "acc_demo_001",
            role: "owner" as const,
            tier: "free" as const,
            createdAt: new Date().toISOString(),
        };

        const mockToken = "demo_token_" + Date.now();

        const mockWallet = {
            balance: 5.00,
            currency: "USD",
            status: "healthy" as const,
            autoPayEnabled: false,
            lastUpdated: new Date().toISOString(),
        };

        // Set auth state
        login(mockUser, mockToken, mockWallet);

        // Navigate to dashboard
        router.push("/dashboard");
    };


    return (
        <div className="min-h-screen bg-black flex flex-col">
            {/* Main Content */}
            <div className="flex-1 flex flex-col items-center justify-center px-4">
                {/* Logo */}
                <div className="mb-8 text-center">
                    <div className="flex items-center justify-center gap-3 mb-6">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#00D4AA] to-[#00F5C8] flex items-center justify-center">
                            <Mic2 className="w-7 h-7 text-black" />
                        </div>
                    </div>
                    <h1 className="text-2xl font-semibold text-white mb-2">
                        Sign in to continue building the
                        <br />
                        next generation of Voice AI agents
                    </h1>
                </div>

                {/* Login Card */}
                <div className="w-full max-w-md">
                    {/* Traffic Light Dots + Demo Link */}
                    <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center gap-1.5">
                            <div className="w-3 h-3 rounded-full bg-[#FF4757]" />
                            <div className="w-3 h-3 rounded-full bg-[#FFB347]" />
                            <div className="w-3 h-3 rounded-full bg-[#00D4AA]" />
                        </div>
                        <Link
                            href="#"
                            className="text-sm text-[#00D4AA] hover:text-[#00F5C8] flex items-center gap-1 transition-colors"
                        >
                            view-demo
                            <ExternalLink className="w-3 h-3" />
                        </Link>
                    </div>

                    {/* Form */}
                    <form onSubmit={handleLogin} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-[#B0B0B0] mb-2">
                                Email
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@example.com"
                                className="w-full px-4 py-3 bg-[#1A1A1A] border border-white/10 rounded-lg text-white text-sm placeholder:text-[#6B6B6B] focus:outline-none focus:ring-2 focus:ring-[#00D4AA] focus:border-transparent transition-all"
                                required
                            />
                        </div>

                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <label className="block text-sm font-medium text-[#B0B0B0]">
                                    Password
                                </label>
                                <Link
                                    href="/forgot-password"
                                    className="text-sm text-[#00D4AA] hover:text-[#00F5C8] transition-colors"
                                >
                                    Forgot password?
                                </Link>
                            </div>
                            <div className="relative">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    className="w-full px-4 py-3 bg-[#1A1A1A] border border-white/10 rounded-lg text-white text-sm placeholder:text-[#6B6B6B] focus:outline-none focus:ring-2 focus:ring-[#00D4AA] focus:border-transparent transition-all pr-10"
                                    required
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6B6B6B] hover:text-white transition-colors"
                                >
                                    {showPassword ? (
                                        <EyeOff className="w-4 h-4" />
                                    ) : (
                                        <Eye className="w-4 h-4" />
                                    )}
                                </button>
                            </div>
                        </div>

                        <Button
                            type="submit"
                            variant="primary"
                            size="lg"
                            className="w-full"
                            isLoading={isLoading}
                        >
                            Sign in to your account →
                        </Button>
                    </form>

                    {/* Divider */}
                    <div className="relative my-6">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-white/10" />
                        </div>
                        <div className="relative flex justify-center text-sm">
                            <span className="px-3 bg-black text-[#6B6B6B]">OR CONTINUE WITH</span>
                        </div>
                    </div>

                    {/* OAuth Buttons */}
                    <div className="flex gap-4">
                        <Button
                            variant="secondary"
                            className="flex-1 py-3"
                            onClick={() => {/* GitHub OAuth */ }}
                        >
                            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                            </svg>
                            GitHub
                        </Button>
                        <Button
                            variant="secondary"
                            className="flex-1 py-3"
                            onClick={() => {/* Google OAuth */ }}
                        >
                            <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                            </svg>
                            Google
                        </Button>
                    </div>

                    {/* Terms */}
                    <p className="text-center text-xs text-[#6B6B6B] mt-6">
                        By signing in, you agree to our{" "}
                        <Link href="/terms" className="text-[#00D4AA] hover:underline">
                            Terms of Service
                        </Link>
                        {" "}and{" "}
                        <Link href="/privacy" className="text-[#00D4AA] hover:underline">
                            Privacy Policy
                        </Link>
                    </p>

                    {/* Sign Up Link */}
                    <p className="text-center text-sm text-[#B0B0B0] mt-8">
                        New to Sunona?{" "}
                        <Link
                            href="/signup"
                            className="text-[#00D4AA] hover:text-[#00F5C8] font-medium transition-colors"
                        >
                            Create account →
                        </Link>
                    </p>
                </div>
            </div>

            {/* Footer */}
            <footer className="py-6 border-t border-white/10">
                <div className="flex items-center justify-center gap-6 text-sm text-[#6B6B6B]">
                    <Link href="/docs" className="hover:text-white flex items-center gap-1 transition-colors">
                        📄 Docs
                    </Link>
                    <Link href="#" className="hover:text-white flex items-center gap-1 transition-colors">
                        ⚡ Status
                    </Link>
                    <Link href="/" className="hover:text-white flex items-center gap-1 transition-colors">
                        🌐 Website
                    </Link>
                    <Link href="#" className="hover:text-white flex items-center gap-1 transition-colors">
                        🤖 LLMs.txt
                    </Link>
                </div>
                <p className="text-center text-xs text-[#6B6B6B] mt-4">
                    © 2025 Sunona Inc.
                </p>
            </footer>

            {/* Talk to us Widget */}
            <button className="fixed bottom-6 right-6 flex items-center gap-2 px-4 py-2.5 bg-[#00D4AA] text-black font-medium rounded-full shadow-lg hover:shadow-[0_0_20px_rgba(0,212,170,0.4)] transition-all">
                <MessageCircle className="w-5 h-5" />
                Talk to us
            </button>
        </div>
    );
}
