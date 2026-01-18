/**
 * 404 Not Found Page
 */
import Link from "next/link";
import { FileQuestion, Home, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

export default function NotFound() {
    return (
        <div className="min-h-screen bg-[#0F0F1A] flex items-center justify-center p-4">
            <Card variant="bordered" className="max-w-md w-full text-center">
                <CardContent className="p-8">
                    <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-purple-500/10 mb-6">
                        <FileQuestion className="h-10 w-10 text-purple-400" />
                    </div>
                    <h1 className="text-4xl font-bold text-white mb-2">404</h1>
                    <h2 className="text-xl font-semibold text-gray-300 mb-4">
                        Page Not Found
                    </h2>
                    <p className="text-gray-400 mb-8">
                        The page you&apos;re looking for doesn&apos;t exist or has been moved.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <Link href="/">
                            <Button leftIcon={<Home className="h-4 w-4" />}>
                                Go Home
                            </Button>
                        </Link>
                        <Link href="/dashboard">
                            <Button variant="outline" leftIcon={<ArrowLeft className="h-4 w-4" />}>
                                Dashboard
                            </Button>
                        </Link>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
