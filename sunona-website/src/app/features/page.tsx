/**
 * Features Page - Sunona Style
 * Comprehensive features overview
 */

import Link from "next/link";
import { ArrowRight, Check } from "lucide-react";

const featureCategories = [
    {
        title: "Voice AI Capabilities",
        features: [
            {
                icon: "💬",
                title: "Natural Conversations",
                description: "Agents understand interruptions, handle overlapping speech, and reply with <300ms latency for human-like interactions.",
                highlights: ["Low latency", "Interruption handling", "Natural flow"],
            },
            {
                icon: "🌍",
                title: "Multilingual Support",
                description: "Converse fluently in 10+ Indian and Foreign Languages including Hindi, Tamil, Telugu, Bengali, Marathi, and Hinglish.",
                highlights: ["10+ languages", "Regional accents", "Code-switching"],
            },
            {
                icon: "🎚️",
                title: "Model Switching",
                description: "Run each call with models suited best for your use case. Switch between providers dynamically based on requirements.",
                highlights: ["Dynamic selection", "A/B testing", "Cost optimization"],
            },
            {
                icon: "🔌",
                title: "Connect Any Model",
                description: "Integrated with 20+ ASR, LLM, and TTS models. Bring your own API keys for maximum flexibility.",
                highlights: ["20+ providers", "BYOK support", "Custom models"],
            },
        ],
    },
    {
        title: "Calling & Telephony",
        features: [
            {
                icon: "📞",
                title: "Bulk Calling at Scale",
                description: "Run campaigns with thousands of AI calls simultaneously. Perfect for outbound sales, surveys, and notifications.",
                highlights: ["Thousands concurrent", "Campaign management", "Rate limiting"],
            },
            {
                icon: "👤",
                title: "Human-in-the-Loop",
                description: "Transfer call to a real agent instantly when needed. Seamless handoff with full context preservation.",
                highlights: ["Warm transfer", "Context sharing", "Fallback handling"],
            },
            {
                icon: "📱",
                title: "Multi-Telephony Support",
                description: "Works with Twilio, Plivo, Exotel, and other telephony providers. Use your existing phone infrastructure.",
                highlights: ["Twilio", "Plivo", "Exotel"],
            },
            {
                icon: "🔊",
                title: "Voicemail Detection",
                description: "Automatically detect voicemails and handle them appropriately. Leave messages or retry later.",
                highlights: ["Auto-detection", "Custom messages", "Retry logic"],
            },
        ],
    },
    {
        title: "Integration & Automation",
        features: [
            {
                icon: "⚡",
                title: "Custom API Triggers",
                description: "Call external APIs in real-time during a live conversation. Fetch data, update CRMs, and trigger actions.",
                highlights: ["Real-time API calls", "Webhook support", "Custom logic"],
            },
            {
                icon: "🔄",
                title: "Workflow Integration",
                description: "Easy to integrate with n8n, Make.com, Zapier, and other automation tools for end-to-end workflows.",
                highlights: ["n8n", "Zapier", "Make.com"],
            },
            {
                icon: "📊",
                title: "Analytics & Insights",
                description: "Detailed call analytics, transcripts, and sentiment analysis. Track performance and optimize agents.",
                highlights: ["Call transcripts", "Sentiment analysis", "Custom metrics"],
            },
            {
                icon: "🎣",
                title: "Webhooks",
                description: "Receive real-time updates on call events. Integrate with your existing systems seamlessly.",
                highlights: ["Real-time events", "Custom payloads", "Retry logic"],
            },
        ],
    },
    {
        title: "Enterprise & Security",
        features: [
            {
                icon: "🏢",
                title: "Enterprise Plans",
                description: "Best-in-class pricing and Forward Deployed service. Dedicated support and custom SLAs.",
                highlights: ["Volume discounts", "Dedicated support", "Custom SLA"],
            },
            {
                icon: "🔒",
                title: "100% Data Privacy",
                description: "India / USA specific data residency, on-prem deployment options. SOC2 and GDPR compliant.",
                highlights: ["Data residency", "On-prem option", "Compliance"],
            },
            {
                icon: "👥",
                title: "Subaccounts",
                description: "Manage multiple teams or clients with subaccounts. Track usage and billing separately.",
                highlights: ["Team management", "Usage tracking", "Separate billing"],
            },
            {
                icon: "🔐",
                title: "SSO & SAML",
                description: "Single sign-on with your existing identity provider. SAML 2.0 support for enterprise security.",
                highlights: ["SSO support", "SAML 2.0", "Role-based access"],
            },
        ],
    },
];

export default function FeaturesPage() {
    return (
        <div className="min-h-screen bg-[#0a0a0f] text-white">
            {/* Navigation */}
            <nav className="sticky top-0 z-50 bg-[#0a0a0f]/90 backdrop-blur-lg border-b border-white/5">
                <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center">
                            <span className="text-white font-bold text-sm">S</span>
                        </div>
                        <span className="text-xl font-bold">SUNONA</span>
                    </Link>

                    <div className="flex items-center gap-4">
                        <Link href="/login" className="text-gray-300 hover:text-white text-sm">Login</Link>
                        <Link
                            href="/signup"
                            className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-black font-medium rounded-lg text-sm"
                        >
                            Get Started
                        </Link>
                    </div>
                </div>
            </nav>

            {/* Hero */}
            <section className="py-20 px-6 text-center">
                <span className="inline-block px-4 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-full text-cyan-400 text-sm font-medium mb-4">
                    FEATURES
                </span>
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                    Features That Power Real Voice Agents
                </h1>
                <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                    With integrated speech, telephony, and APIs, Sunona equips you with everything
                    required to move from idea to live deployment quickly and securely.
                </p>
            </section>

            {/* Feature Categories */}
            {featureCategories.map((category) => (
                <section key={category.title} className="py-16 px-6 border-t border-white/5">
                    <div className="max-w-6xl mx-auto">
                        <h2 className="text-2xl font-bold mb-12 text-center">{category.title}</h2>

                        <div className="grid md:grid-cols-2 gap-8">
                            {category.features.map((feature) => (
                                <div
                                    key={feature.title}
                                    className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-cyan-500/30 transition-colors"
                                >
                                    <div className="flex items-start gap-4">
                                        <div className="w-12 h-12 bg-cyan-500/10 rounded-lg flex items-center justify-center text-2xl flex-shrink-0">
                                            {feature.icon}
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                                            <p className="text-sm text-gray-400 mb-4">{feature.description}</p>
                                            <div className="flex flex-wrap gap-2">
                                                {feature.highlights.map((h) => (
                                                    <span
                                                        key={h}
                                                        className="inline-flex items-center gap-1 text-xs text-cyan-400"
                                                    >
                                                        <Check className="w-3 h-3" />
                                                        {h}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </section>
            ))}

            {/* CTA */}
            <section className="py-20 px-6 text-center bg-gradient-to-t from-cyan-500/5 to-transparent">
                <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
                <p className="text-gray-400 mb-8">
                    Start building voice agents in minutes with our free tier.
                </p>
                <Link
                    href="/signup"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg"
                >
                    Start Free
                    <ArrowRight className="w-4 h-4" />
                </Link>
            </section>

            {/* Footer */}
            <footer className="py-8 px-6 border-t border-white/10 text-center text-sm text-gray-500">
                <p>© 2025 Sunona Inc. All Rights Reserved.</p>
            </footer>
        </div>
    );
}
