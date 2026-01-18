/**
 * Agent Builder - New Agent Page
 * Multi-step wizard for creating new agents
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
    ArrowLeft,
    ArrowRight,
    Check,
    Briefcase,
    User,
    Volume2,
    Brain,
    FileText,
    Database,
    Phone,
    Rocket,
    Sparkles,
    Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

// Agent templates
const templates = [
    {
        id: "lead_qualification",
        name: "Lead Qualification",
        description: "Identify and qualify potential customers",
        icon: Briefcase,
        color: "purple",
    },
    {
        id: "customer_support",
        name: "Customer Support",
        description: "Answer customer queries and resolve issues",
        icon: User,
        color: "blue",
    },
    {
        id: "appointment_booking",
        name: "Appointment Booking",
        description: "Book appointments and send reminders",
        icon: Sparkles,
        color: "emerald",
    },
    {
        id: "survey_feedback",
        name: "Survey & Feedback",
        description: "Gather survey responses and feedback",
        icon: FileText,
        color: "amber",
    },
    {
        id: "outreach",
        name: "Sales Outreach",
        description: "Make outbound sales calls",
        icon: Zap,
        color: "rose",
    },
    {
        id: "custom",
        name: "Custom Agent",
        description: "Build a custom agent from scratch",
        icon: Brain,
        color: "cyan",
    },
];

// TTS Providers
const ttsProviders = [
    { id: "edge", name: "Edge TTS", cost: "FREE", badge: "Default" },
    { id: "elevenlabs", name: "ElevenLabs", cost: "$0.18/1K", badge: "Realistic" },
    { id: "deepgram", name: "Deepgram Aura", cost: "$0.0065/1K", badge: "Fast" },
    { id: "openai", name: "OpenAI TTS", cost: "$0.015/1K", badge: null },
    { id: "cartesia", name: "Cartesia", cost: "$0.10/1K", badge: "Low Latency" },
    { id: "playht", name: "PlayHT", cost: "$0.15/1K", badge: null },
];

// LLM Models
const llmModels = [
    { id: "gpt-4o", name: "GPT-4o", provider: "OpenAI", badge: "Recommended" },
    { id: "gpt-4o-mini", name: "GPT-4o-mini", provider: "OpenAI", badge: "Budget" },
    { id: "claude-3.5-sonnet", name: "Claude 3.5 Sonnet", provider: "Anthropic", badge: null },
    { id: "gemini-pro", name: "Gemini Pro", provider: "Google", badge: null },
    { id: "llama-3.1-70b", name: "Llama 3.1 70B", provider: "Meta", badge: "Open Source" },
];

// Steps
const steps = [
    { id: 1, name: "Template", icon: Sparkles },
    { id: 2, name: "Persona", icon: User },
    { id: 3, name: "Voice", icon: Volume2 },
    { id: 4, name: "LLM", icon: Brain },
    { id: 5, name: "Prompt", icon: FileText },
    { id: 6, name: "Deploy", icon: Rocket },
];

export default function NewAgentPage() {
    const router = useRouter();
    const [currentStep, setCurrentStep] = React.useState(1);
    const [isDeploying, setIsDeploying] = React.useState(false);

    // Form state
    const [agentConfig, setAgentConfig] = React.useState({
        template: "",
        name: "",
        description: "",
        persona: "",
        ttsProvider: "edge",
        llmModel: "gpt-4o-mini",
        systemPrompt: "",
    });

    const updateConfig = (key: string, value: string) => {
        setAgentConfig((prev) => ({ ...prev, [key]: value }));
    };

    const handleNext = () => {
        if (currentStep < steps.length) {
            setCurrentStep(currentStep + 1);
        }
    };

    const handleBack = () => {
        if (currentStep > 1) {
            setCurrentStep(currentStep - 1);
        }
    };

    const handleDeploy = async () => {
        setIsDeploying(true);
        // Simulate deployment
        await new Promise((resolve) => setTimeout(resolve, 2000));
        setIsDeploying(false);
        router.push("/dashboard/agents");
    };

    const canProceed = () => {
        switch (currentStep) {
            case 1:
                return !!agentConfig.template;
            case 2:
                return !!agentConfig.name;
            case 3:
                return !!agentConfig.ttsProvider;
            case 4:
                return !!agentConfig.llmModel;
            case 5:
                return true; // Prompt is optional
            default:
                return true;
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link href="/dashboard/agents">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </Link>
                <div>
                    <h1 className="text-2xl font-bold text-white">Create New Agent</h1>
                    <p className="text-gray-400">
                        Step {currentStep} of {steps.length}: {steps[currentStep - 1].name}
                    </p>
                </div>
            </div>

            {/* Progress Steps */}
            <div className="flex items-center justify-between">
                {steps.map((step, index) => (
                    <React.Fragment key={step.id}>
                        <div className="flex flex-col items-center gap-2">
                            <div
                                className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors ${currentStep > step.id
                                        ? "bg-emerald-500 text-white"
                                        : currentStep === step.id
                                            ? "bg-purple-500 text-white"
                                            : "bg-[#252540] text-gray-500"
                                    }`}
                            >
                                {currentStep > step.id ? (
                                    <Check className="h-5 w-5" />
                                ) : (
                                    <step.icon className="h-5 w-5" />
                                )}
                            </div>
                            <span
                                className={`text-xs hidden sm:block ${currentStep >= step.id ? "text-white" : "text-gray-500"
                                    }`}
                            >
                                {step.name}
                            </span>
                        </div>
                        {index < steps.length - 1 && (
                            <div
                                className={`flex-1 h-0.5 mx-2 ${currentStep > step.id ? "bg-emerald-500" : "bg-[#374151]"
                                    }`}
                            />
                        )}
                    </React.Fragment>
                ))}
            </div>

            {/* Step Content */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentStep}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                >
                    {/* Step 1: Template Selection */}
                    {currentStep === 1 && (
                        <div className="space-y-6">
                            <h2 className="text-lg font-semibold text-white">
                                What type of agent do you want to create?
                            </h2>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                {templates.map((template) => (
                                    <Card
                                        key={template.id}
                                        variant={agentConfig.template === template.id ? "elevated" : "bordered"}
                                        className={`cursor-pointer transition-all ${agentConfig.template === template.id
                                                ? "border-purple-500 ring-2 ring-purple-500/20"
                                                : "hover:border-gray-600"
                                            }`}
                                        onClick={() => updateConfig("template", template.id)}
                                    >
                                        <CardContent className="p-4">
                                            <div className={`w-10 h-10 rounded-lg bg-${template.color}-500/10 flex items-center justify-center mb-3`}>
                                                <template.icon className={`h-5 w-5 text-${template.color}-400`} />
                                            </div>
                                            <h3 className="font-medium text-white mb-1">{template.name}</h3>
                                            <p className="text-sm text-gray-400">{template.description}</p>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Step 2: Persona */}
                    {currentStep === 2 && (
                        <div className="space-y-6">
                            <h2 className="text-lg font-semibold text-white">
                                Configure your agent&apos;s identity
                            </h2>
                            <Card variant="default">
                                <CardContent className="p-6 space-y-4">
                                    <Input
                                        label="Agent Name"
                                        placeholder="e.g., Sales Assistant"
                                        value={agentConfig.name}
                                        onChange={(e) => updateConfig("name", e.target.value)}
                                    />
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            Description
                                        </label>
                                        <textarea
                                            placeholder="Describe what this agent does..."
                                            value={agentConfig.description}
                                            onChange={(e) => updateConfig("description", e.target.value)}
                                            rows={3}
                                            className="w-full rounded-lg border bg-[#1A1A2E] px-4 py-3 text-white placeholder:text-gray-500 border-[#374151] focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-300 mb-2">
                                            Persona (How the agent should behave)
                                        </label>
                                        <textarea
                                            placeholder="e.g., You are a friendly and professional sales representative..."
                                            value={agentConfig.persona}
                                            onChange={(e) => updateConfig("persona", e.target.value)}
                                            rows={4}
                                            className="w-full rounded-lg border bg-[#1A1A2E] px-4 py-3 text-white placeholder:text-gray-500 border-[#374151] focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20"
                                        />
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}

                    {/* Step 3: Voice Selection */}
                    {currentStep === 3 && (
                        <div className="space-y-6">
                            <h2 className="text-lg font-semibold text-white">
                                Select a voice provider
                            </h2>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                                {ttsProviders.map((provider) => (
                                    <Card
                                        key={provider.id}
                                        variant={agentConfig.ttsProvider === provider.id ? "elevated" : "bordered"}
                                        className={`cursor-pointer transition-all ${agentConfig.ttsProvider === provider.id
                                                ? "border-purple-500 ring-2 ring-purple-500/20"
                                                : "hover:border-gray-600"
                                            }`}
                                        onClick={() => updateConfig("ttsProvider", provider.id)}
                                    >
                                        <CardContent className="p-4">
                                            <div className="flex items-center justify-between mb-2">
                                                <h3 className="font-medium text-white">{provider.name}</h3>
                                                {provider.badge && (
                                                    <Badge
                                                        variant={provider.cost === "FREE" ? "success" : "purple"}
                                                        size="sm"
                                                    >
                                                        {provider.badge}
                                                    </Badge>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-400">{provider.cost}</p>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Step 4: LLM Selection */}
                    {currentStep === 4 && (
                        <div className="space-y-6">
                            <h2 className="text-lg font-semibold text-white">
                                Select an LLM model
                            </h2>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {llmModels.map((model) => (
                                    <Card
                                        key={model.id}
                                        variant={agentConfig.llmModel === model.id ? "elevated" : "bordered"}
                                        className={`cursor-pointer transition-all ${agentConfig.llmModel === model.id
                                                ? "border-purple-500 ring-2 ring-purple-500/20"
                                                : "hover:border-gray-600"
                                            }`}
                                        onClick={() => updateConfig("llmModel", model.id)}
                                    >
                                        <CardContent className="p-4">
                                            <div className="flex items-center justify-between mb-1">
                                                <h3 className="font-medium text-white">{model.name}</h3>
                                                {model.badge && (
                                                    <Badge variant="purple" size="sm">
                                                        {model.badge}
                                                    </Badge>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-400">{model.provider}</p>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Step 5: System Prompt */}
                    {currentStep === 5 && (
                        <div className="space-y-6">
                            <h2 className="text-lg font-semibold text-white">
                                Customize the system prompt (optional)
                            </h2>
                            <Card variant="default">
                                <CardContent className="p-6">
                                    <textarea
                                        placeholder="Enter custom instructions for your agent..."
                                        value={agentConfig.systemPrompt}
                                        onChange={(e) => updateConfig("systemPrompt", e.target.value)}
                                        rows={10}
                                        className="w-full rounded-lg border bg-[#1A1A2E] px-4 py-3 text-white placeholder:text-gray-500 border-[#374151] focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 font-mono text-sm"
                                    />
                                    <p className="text-sm text-gray-500 mt-2">
                                        Leave empty to use the default template prompt.
                                    </p>
                                </CardContent>
                            </Card>
                        </div>
                    )}

                    {/* Step 6: Deploy */}
                    {currentStep === 6 && (
                        <div className="space-y-6">
                            <h2 className="text-lg font-semibold text-white">
                                Review and deploy your agent
                            </h2>
                            <Card variant="default">
                                <CardContent className="p-6 space-y-4">
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-sm text-gray-500">Template</p>
                                            <p className="text-white capitalize">
                                                {agentConfig.template.replace(/_/g, " ")}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Agent Name</p>
                                            <p className="text-white">{agentConfig.name || "—"}</p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">Voice Provider</p>
                                            <p className="text-white">
                                                {ttsProviders.find((p) => p.id === agentConfig.ttsProvider)?.name}
                                            </p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-500">LLM Model</p>
                                            <p className="text-white">
                                                {llmModels.find((m) => m.id === agentConfig.llmModel)?.name}
                                            </p>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </div>
                    )}
                </motion.div>
            </AnimatePresence>

            {/* Navigation */}
            <div className="flex items-center justify-between pt-4 border-t border-[#374151]/50">
                <Button
                    variant="outline"
                    onClick={handleBack}
                    disabled={currentStep === 1}
                    leftIcon={<ArrowLeft className="h-4 w-4" />}
                >
                    Back
                </Button>

                {currentStep === steps.length ? (
                    <Button
                        onClick={handleDeploy}
                        isLoading={isDeploying}
                        leftIcon={<Rocket className="h-4 w-4" />}
                    >
                        Deploy Agent
                    </Button>
                ) : (
                    <Button
                        onClick={handleNext}
                        disabled={!canProceed()}
                        rightIcon={<ArrowRight className="h-4 w-4" />}
                    >
                        Continue
                    </Button>
                )}
            </div>
        </div>
    );
}
