/**
 * Error Boundary Component
 * Catches and displays errors gracefully
 */
"use client";

import * as React from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Link from "next/link";

interface ErrorBoundaryProps {
    children: React.ReactNode;
    fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error("Error caught by boundary:", error, errorInfo);
    }

    handleRetry = () => {
        this.setState({ hasError: false, error: null });
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-[400px] flex items-center justify-center p-6">
                    <Card variant="bordered" className="max-w-md w-full border-red-500/20">
                        <CardContent className="p-8 text-center">
                            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-500/10 mb-6">
                                <AlertTriangle className="h-8 w-8 text-red-400" />
                            </div>
                            <h2 className="text-xl font-bold text-white mb-2">
                                Something went wrong
                            </h2>
                            <p className="text-gray-400 mb-6">
                                An unexpected error occurred. Please try again or return to the homepage.
                            </p>
                            {this.state.error && (
                                <pre className="text-xs text-left bg-[#0F0F1A] p-3 rounded-lg mb-6 overflow-auto max-h-32 text-red-400">
                                    {this.state.error.message}
                                </pre>
                            )}
                            <div className="flex items-center justify-center gap-3">
                                <Button
                                    variant="outline"
                                    onClick={this.handleRetry}
                                    leftIcon={<RefreshCw className="h-4 w-4" />}
                                >
                                    Try Again
                                </Button>
                                <Link href="/">
                                    <Button leftIcon={<Home className="h-4 w-4" />}>
                                        Go Home
                                    </Button>
                                </Link>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            );
        }

        return this.props.children;
    }
}

// Functional error component for use with Next.js error pages
export function ErrorDisplay({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-[#0F0F1A]">
            <Card variant="bordered" className="max-w-md w-full border-red-500/20">
                <CardContent className="p-8 text-center">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-500/10 mb-6">
                        <AlertTriangle className="h-8 w-8 text-red-400" />
                    </div>
                    <h2 className="text-xl font-bold text-white mb-2">
                        Something went wrong
                    </h2>
                    <p className="text-gray-400 mb-6">
                        {error.message || "An unexpected error occurred."}
                    </p>
                    <div className="flex items-center justify-center gap-3">
                        <Button
                            variant="outline"
                            onClick={reset}
                            leftIcon={<RefreshCw className="h-4 w-4" />}
                        >
                            Try Again
                        </Button>
                        <Link href="/">
                            <Button leftIcon={<Home className="h-4 w-4" />}>
                                Go Home
                            </Button>
                        </Link>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
