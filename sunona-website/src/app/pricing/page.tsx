/**
 * Pricing Page - Sunona Voice AI
 * Matches backend pricing: $0.04/min with 20% profit margin
 */

import Link from "next/link";
import { Check, ArrowRight, Zap } from "lucide-react";

const pricingTiers = [
    {
        name: "Pay As You Go",
        description: "No commitment, pay only for what you use",
        price: "$0.04",
        priceNote: "per minute",
        features: [
            "$5 free credits to start",
            "5 concurrent calls",
            "3 AI agents",
            "All voice providers",
            "Basic analytics",
            "Community support",
        ],
        cta: "Get Started Free",
        featured: false,
    },
    {
        name: "Starter",
        description: "Perfect for small teams getting started",
        price: "$199",
        priceNote: "per month",
        features: [
            "5,000 minutes included",
            "10 concurrent calls",
            "5 AI agents",
            "All voice providers",
            "Advanced analytics",
            "Email support",
            "$0.05 overage rate",
        ],
        cta: "Start Free Trial",
        featured: true,
    },
    {
        name: "Growth",
        description: "For growing teams with higher volume",
        price: "$499",
        priceNote: "per month",
        features: [
            "15,000 minutes included",
            "25 concurrent calls",
            "15 AI agents",
            "Priority support",
            "Custom voices",
            "Webhooks & API access",
            "$0.04 overage rate",
        ],
        cta: "Contact Sales",
        featured: false,
    },
];

// Detailed cost breakdown matching backend
const usagePricing = [
    { component: "LLM (Groq Llama)", price: "$0.001", note: "Fastest & cheapest" },
    { component: "STT (Groq Whisper)", price: "$0.004", note: "Real-time transcription" },
    { component: "TTS (Deepgram Aura)", price: "$0.005", note: "Natural voice" },
    { component: "Telephony (Twilio)", price: "$0.014", note: "Global coverage" },
    { component: "Platform Fee", price: "$0.008", note: "Sunona infrastructure" },
    { component: "Total", price: "$0.04/min", note: "All-inclusive rate", isTotal: true },
];

const competitorComparison = [
    { name: "Sunona", price: "$0.04", savings: "—" },
    { name: "Major Competitors", price: "$0.09", savings: "55% cheaper" },
];

const faqs = [
    {
        question: "How does pricing work?",
        answer: "You pay $0.04 per minute of call time. This includes all services: LLM, speech-to-text, text-to-speech, telephony, and platform fees. No hidden costs.",
    },
    {
        question: "Can I bring my own API keys (BYOK)?",
        answer: "Yes! With BYOK, you only pay the platform fee of $0.008/min. Connect your own Groq, Deepgram, or Twilio keys to reduce costs even further.",
    },
    {
        question: "What's included in the free tier?",
        answer: "You get $5 in free credits (125 minutes), 5 concurrent calls, access to all voice agents, and up to 3 AI agents for testing.",
    },
    {
        question: "How do subscription tiers save money?",
        answer: "Starter plan ($199/mo) gives you 5,000 minutes at an effective rate of $0.04/min. Growth plan ($499/mo) gives 15,000 minutes at $0.033/min - great for high volume!",
    },
];


export default function PricingPage() {
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
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                    Simple, Transparent Pricing
                </h1>
                <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                    Start free, scale as you grow. Only pay for what you use.
                </p>
            </section>

            {/* Pricing Cards */}
            <section className="py-12 px-6">
                <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-8">
                    {pricingTiers.map((tier) => (
                        <div
                            key={tier.name}
                            className={`relative rounded-2xl p-8 ${tier.featured
                                ? "bg-gradient-to-b from-cyan-500/20 to-transparent border-2 border-cyan-500"
                                : "bg-white/5 border border-white/10"
                                }`}
                        >
                            {tier.featured && (
                                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-cyan-500 text-black text-sm font-medium rounded-full">
                                    Most Popular
                                </div>
                            )}

                            <h3 className="text-xl font-semibold mb-2">{tier.name}</h3>
                            <p className="text-sm text-gray-400 mb-6">{tier.description}</p>

                            <div className="mb-8">
                                <span className="text-4xl font-bold">{tier.price}</span>
                                <span className="text-gray-400 ml-2">/{tier.priceNote}</span>
                            </div>

                            <ul className="space-y-3 mb-8">
                                {tier.features.map((feature) => (
                                    <li key={feature} className="flex items-center gap-3 text-sm">
                                        <Check className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                                        <span className="text-gray-300">{feature}</span>
                                    </li>
                                ))}
                            </ul>

                            <Link
                                href={tier.name === "Enterprise" ? "#contact" : "/signup"}
                                className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg font-medium transition-colors ${tier.featured
                                    ? "bg-cyan-500 hover:bg-cyan-400 text-black"
                                    : "border border-white/20 hover:bg-white/5"
                                    }`}
                            >
                                {tier.cta}
                                <ArrowRight className="w-4 h-4" />
                            </Link>
                        </div>
                    ))}
                </div>
            </section>

            {/* Cost Breakdown Table */}
            <section className="py-20 px-6">
                <div className="max-w-4xl mx-auto">
                    <h2 className="text-2xl font-bold text-center mb-4">Transparent Cost Breakdown</h2>
                    <p className="text-center text-gray-400 mb-8">See exactly what you pay for - no hidden fees</p>

                    <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-white/5">
                                <tr>
                                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Component</th>
                                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Price/Min</th>
                                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-400">Details</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {usagePricing.map((row: any) => (
                                    <tr key={row.component} className={row.isTotal ? "bg-cyan-500/10" : ""}>
                                        <td className={`px-6 py-4 text-sm ${row.isTotal ? "font-bold" : ""}`}>{row.component}</td>
                                        <td className={`px-6 py-4 text-sm ${row.isTotal ? "text-cyan-400 font-bold" : "text-cyan-400"}`}>{row.price}</td>
                                        <td className="px-6 py-4 text-sm text-gray-400">{row.note}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <p className="text-center text-sm text-gray-500 mt-4">
                        💡 Use <span className="text-cyan-400">BYOK</span> (Bring Your Own Keys) to only pay platform fee of $0.008/min
                    </p>
                </div>
            </section>

            {/* Competitor Comparison */}
            <section className="py-12 px-6">
                <div className="max-w-3xl mx-auto">
                    <h2 className="text-2xl font-bold text-center mb-8">How We Compare</h2>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {competitorComparison.map((comp) => (
                            <div
                                key={comp.name}
                                className={`p-4 rounded-xl text-center ${comp.name === "Sunona"
                                    ? "bg-gradient-to-b from-cyan-500/20 to-transparent border-2 border-cyan-500"
                                    : "bg-white/5 border border-white/10"
                                    }`}
                            >
                                <p className="text-sm text-gray-400">{comp.name}</p>
                                <p className={`text-2xl font-bold ${comp.name === "Sunona" ? "text-cyan-400" : ""}`}>{comp.price}</p>
                                {comp.name === "Sunona" ? (
                                    <p className="text-xs text-cyan-400 mt-1">Best Value</p>
                                ) : (
                                    <p className="text-xs text-green-400 mt-1">{comp.savings}</p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>


            {/* FAQs */}
            <section className="py-20 px-6 bg-gradient-to-b from-transparent to-white/5">
                <div className="max-w-3xl mx-auto">
                    <h2 className="text-2xl font-bold text-center mb-12">Frequently Asked Questions</h2>

                    <div className="space-y-6">
                        {faqs.map((faq) => (
                            <div
                                key={faq.question}
                                className="bg-white/5 border border-white/10 rounded-xl p-6"
                            >
                                <h4 className="font-semibold mb-2">{faq.question}</h4>
                                <p className="text-sm text-gray-400">{faq.answer}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-20 px-6 text-center" id="contact">
                <h2 className="text-3xl font-bold mb-4">Need a Custom Plan?</h2>
                <p className="text-gray-400 mb-8">
                    Talk to our team for volume discounts, custom features, and enterprise support.
                </p>
                <Link
                    href="/signup"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg"
                >
                    Contact Sales
                    <ArrowRight className="w-4 h-4" />
                </Link>
            </section>

            {/* Footer */}
            <footer className="py-8 px-6 border-t border-white/10 text-center text-sm text-gray-500">
                <p>© 2026 Sunona Inc. All Rights Reserved.</p>
            </footer>
        </div>
    );
}
