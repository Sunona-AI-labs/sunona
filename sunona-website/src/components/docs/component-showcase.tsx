"use client";

import * as React from "react";
import { Check, Copy, Code as CodeIcon, Eye } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface ComponentShowcaseProps {
    title: string;
    description?: string;
    code: string;
    children: React.ReactNode;
}

export function ComponentShowcase({ title, description, code, children }: ComponentShowcaseProps) {
    const [view, setView] = React.useState<"preview" | "code">("preview");
    const [copied, setCopied] = React.useState(false);

    const copyCode = () => {
        navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="mb-12">
            <div className="flex items-center justify-between mb-4">
                <div>
                    <h3 className="text-xl font-semibold text-white">{title}</h3>
                    {description && <p className="text-zinc-500 text-sm mt-1">{description}</p>}
                </div>
                <div className="flex items-center gap-2 bg-zinc-900/50 p-1 rounded-lg border border-white/5">
                    <button
                        onClick={() => setView("preview")}
                        className={cn(
                            "flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md transition-all",
                            view === "preview" ? "bg-zinc-800 text-white shadow-sm" : "text-zinc-500 hover:text-zinc-300"
                        )}
                    >
                        <Eye className="w-3.5 h-3.5" />
                        Preview
                    </button>
                    <button
                        onClick={() => setView("code")}
                        className={cn(
                            "flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md transition-all",
                            view === "code" ? "bg-zinc-800 text-white shadow-sm" : "text-zinc-500 hover:text-zinc-300"
                        )}
                    >
                        <CodeIcon className="w-3.5 h-3.5" />
                        Code
                    </button>
                </div>
            </div>

            <div className="relative group">
                {view === "preview" ? (
                    <div className="min-h-[200px] flex items-center justify-center p-8 bg-zinc-900/30 border border-white/5 rounded-xl backdrop-blur-sm relative overflow-hidden">
                        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_120%,rgba(37,99,235,0.05),transparent)] pointer-events-none" />
                        <div className="relative z-10 flex flex-wrap items-center justify-center gap-6">
                            {children}
                        </div>
                    </div>
                ) : (
                    <div className="relative">
                        <pre className="p-6 bg-zinc-950 border border-white/10 rounded-xl overflow-x-auto font-mono text-sm text-zinc-300 leading-relaxed">
                            <code>{code}</code>
                        </pre>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={copyCode}
                            className="absolute top-4 right-4 text-zinc-500 hover:text-white hover:bg-white/5"
                        >
                            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                        </Button>
                    </div>
                )}
            </div>
        </div>
    );
}
