/**
 * Signup Page - Sunona Dark Industrial AI Theme
 * User registration
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Mic2, Eye, EyeOff, ArrowRight, Github, Chrome, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function SignupPage() {
    const router = useRouter();
    const [name, setName] = React.useState("");
    const [email, setEmail] = React.useState("");
    const [password, setPassword] = React.useState("");
    const [showPassword, setShowPassword] = React.useState(false);
    const [isLoading, setIsLoading] = React.useState(false);
    const [agreedToTerms, setAgreedToTerms] = React.useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        // Simulate signup
        await new Promise((resolve) => setTimeout(resolve, 1500));
        router.push("/dashboard");
    };

    const features = [
        "Create unlimited AI voice agents",
        "40+ integrations for STT, TTS, LLM",
        "Enterprise-grade telephony",
        "Real-time analytics dashboard",
    ];

    return (
        <div className="min-h-screen bg-black flex">
            {/* Left Column - Form */}
            <div className="flex-1 flex flex-col justify-center px-8 lg:px-16 py-12">
                <div className="w-full max-w-md mx-auto">
                    {/* Logo */}
                    <Link href="/" className="flex items-center gap-2 mb-8">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00D4AA] to-[#00F5C8] flex items-center justify-center">
                            <Mic2 className="w-6 h-6 text-black" />
                        </div>
                        <span className="text-xl font-bold text-white">Sunona</span>
                    </Link>

                    <h1 className="text-2xl font-bold text-white mb-2">
                        Create your account
                    </h1>
                    <p className="text-[#B0B0B0] mb-8">
                        Start building AI voice agents in minutes
                    </p>

                    {/* OAuth Buttons */}
                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <button className="flex items-center justify-center gap-2 px-4 py-3 bg-[#111111] border border-white/10 rounded-lg text-white hover:bg-white/5 transition-colors">
                            <Github className="w-5 h-5" />
                            <span className="text-sm">GitHub</span>
                        </button>
                        <button className="flex items-center justify-center gap-2 px-4 py-3 bg-[#111111] border border-white/10 rounded-lg text-white hover:bg-white/5 transition-colors">
                            <Chrome className="w-5 h-5" />
                            <span className="text-sm">Google</span>
                        </button>
                    </div>

                    <div className="flex items-center gap-3 mb-6">
                        <div className="flex-1 h-px bg-white/10" />
                        <span className="text-xs text-[#6B6B6B]">or continue with email</span>
                        <div className="flex-1 h-px bg-white/10" />
                    </div>

                    {/* Form */}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-[#B0B0B0] mb-2">
                                Full name
                            </label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="John Doe"
                                required
                                className="w-full px-4 py-3 bg-[#111111] border border-white/10 rounded-lg text-white placeholder:text-[#6B6B6B] focus:outline-none focus:ring-2 focus:ring-[#00D4AA] focus:border-transparent transition-all"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-[#B0B0B0] mb-2">
                                Email address
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="you@company.com"
                                required
                                className="w-full px-4 py-3 bg-[#111111] border border-white/10 rounded-lg text-white placeholder:text-[#6B6B6B] focus:outline-none focus:ring-2 focus:ring-[#00D4AA] focus:border-transparent transition-all"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-[#B0B0B0] mb-2">
                                Password
                            </label>
                            <div className="relative">
                                <input
                                    type={showPassword ? "text" : "password"}
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    placeholder="••••••••"
                                    required
                                    minLength={8}
                                    className="w-full px-4 py-3 bg-[#111111] border border-white/10 rounded-lg text-white placeholder:text-[#6B6B6B] focus:outline-none focus:ring-2 focus:ring-[#00D4AA] focus:border-transparent transition-all pr-12"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-[#6B6B6B] hover:text-white"
                                >
                                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                            </div>
                            <p className="text-xs text-[#6B6B6B] mt-1">Minimum 8 characters</p>
                        </div>

                        <div className="flex items-start gap-3">
                            <input
                                type="checkbox"
                                id="terms"
                                checked={agreedToTerms}
                                onChange={(e) => setAgreedToTerms(e.target.checked)}
                                className="mt-1 w-4 h-4 rounded border-white/20 bg-[#111111] text-[#00D4AA] focus:ring-[#00D4AA]"
                            />
                            <label htmlFor="terms" className="text-sm text-[#B0B0B0]">
                                I agree to the{" "}
                                <Link href="/terms" className="text-[#00D4AA] hover:underline">
                                    Terms of Service
                                </Link>{" "}
                                and{" "}
                                <Link href="/privacy" className="text-[#00D4AA] hover:underline">
                                    Privacy Policy
                                </Link>
                            </label>
                        </div>

                        <Button
                            type="submit"
                            className="w-full"
                            disabled={isLoading || !agreedToTerms}
                            isLoading={isLoading}
                        >
                            Create account
                            <ArrowRight className="w-4 h-4 ml-2" />
                        </Button>
                    </form>

                    <p className="text-sm text-[#6B6B6B] text-center mt-6">
                        Already have an account?{" "}
                        <Link href="/login" className="text-[#00D4AA] hover:underline">
                            Sign in
                        </Link>
                    </p>
                </div>
            </div>

            {/* Right Column - Features */}
            <div className="hidden lg:flex flex-1 bg-gradient-to-br from-[#111111] to-[#0A0A0A] border-l border-white/10 items-center justify-center p-16">
                <div className="max-w-md">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#00D4AA] to-[#00F5C8] flex items-center justify-center mb-8">
                        <Mic2 className="w-8 h-8 text-black" />
                    </div>

                    <h2 className="text-3xl font-bold text-white mb-4">
                        Voice AI Built for Scale
                    </h2>
                    <p className="text-[#B0B0B0] mb-8">
                        Join 500+ companies using Sunona to power their voice AI stack across 10+ Indian languages.
                    </p>

                    <ul className="space-y-4">
                        {features.map((feature) => (
                            <li key={feature} className="flex items-center gap-3">
                                <div className="w-5 h-5 rounded-full bg-[#00D4AA]/10 flex items-center justify-center">
                                    <Check className="w-3 h-3 text-[#00D4AA]" />
                                </div>
                                <span className="text-[#B0B0B0]">{feature}</span>
                            </li>
                        ))}
                    </ul>

                    <div className="mt-12 p-6 bg-white/5 border border-white/10 rounded-xl">
                        <p className="text-sm text-[#B0B0B0] italic mb-4">
                            "Sunona helped us scale from 100 to 10,000 daily calls with ease. The voice quality is incredible."
                        </p>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#9B59B6] to-[#E91E63] flex items-center justify-center text-white font-medium text-sm">
                                RK
                            </div>
                            <div>
                                <p className="text-white font-medium">Rahul Kumar</p>
                                <p className="text-xs text-[#6B6B6B]">CTO, TechStartup</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
