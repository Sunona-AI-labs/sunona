/**
 * Agents Showcase Page - Sunona Style
 * Browse all pre-built AI voice agents by category
 */

import Link from "next/link";
import { Phone, Play, ExternalLink, ArrowRight } from "lucide-react";

const categories = [
    { id: "all", label: "All Agents", count: 12 },
    { id: "ecommerce", label: "Ecommerce", count: 4 },
    { id: "edtech", label: "EdTech", count: 2 },
    { id: "healthtech", label: "Health Tech", count: 2 },
    { id: "bfsi", label: "BFSI", count: 2 },
    { id: "hospitality", label: "Hospitality", count: 2 },
];

const agents = [
    {
        name: "Customer Support Agent",
        category: "ecommerce",
        tags: ["Customer Support", "English"],
        description: "Provides 24/7 inbound call answering for FAQs and customer triage. Handles returns, order status, and general inquiries with natural conversation flow.",
        phone: "+918035317400",
        useCases: ["Order tracking", "Returns & refunds", "FAQ handling", "Ticket creation"],
    },
    {
        name: "Cart Abandonment Agent",
        category: "ecommerce",
        tags: ["Cart Abandonment", "English + Hindi"],
        description: "Calls customers with abandoned items in carts, recovering sales through personalized outreach and special offers.",
        phone: "+918035317449",
        useCases: ["Cart recovery calls", "Discount offers", "Checkout assistance", "Payment support"],
    },
    {
        name: "COD Confirmation Agent",
        category: "ecommerce",
        tags: ["COD Confirmation", "English + Hindi"],
        description: "Confirms cash-on-delivery orders to reduce RTO rates and verify customer intent before dispatch.",
        phone: "+918035317450",
        useCases: ["Order confirmation", "Address verification", "RTO prevention", "Delivery scheduling"],
    },
    {
        name: "Recruitment Agent",
        category: "all",
        tags: ["Recruitment", "English"],
        description: "AI agents that screen, interview, and onboard candidates at scale. Conducts initial rounds with structured questions.",
        phone: "+918035317441",
        useCases: ["Resume screening", "Initial interviews", "Skill assessment", "Scheduling follow-ups"],
    },
    {
        name: "Lead Qualification Agent",
        category: "bfsi",
        tags: ["Lead Qualification", "Hindi"],
        description: "Calls every lead to ask qualifying questions, answer FAQs, and warmly introduce the business to potential customers.",
        phone: "+918035317443",
        useCases: ["Lead scoring", "Qualification questions", "Product introduction", "Appointment booking"],
    },
    {
        name: "Onboarding Agent",
        category: "all",
        tags: ["Onboarding", "English"],
        description: "Conducts personalized guidance calls to warmly onboard users, explain features, and ensure successful activation.",
        phone: "+918035317448",
        useCases: ["Welcome calls", "Feature walkthrough", "Setup assistance", "First-use guidance"],
    },
    {
        name: "Announcements Agent",
        category: "all",
        tags: ["Announcements", "English + Hindi"],
        description: "Broadcasts important announcements, policy updates, and promotional messages to your customer base.",
        phone: "+918035317447",
        useCases: ["Policy updates", "Promotional calls", "Event reminders", "Service announcements"],
    },
    {
        name: "Reminders Agent",
        category: "healthtech",
        tags: ["Reminders", "English + Hindi"],
        description: "Sends automated reminder calls for appointments, payments, renewals, and important deadlines.",
        phone: "+918035317446",
        useCases: ["Appointment reminders", "Payment due dates", "Subscription renewals", "Follow-up calls"],
    },
    {
        name: "Front Desk Agent",
        category: "hospitality",
        tags: ["Front Desk", "English"],
        description: "Handles hotel and restaurant reservations, provides information about amenities, and manages booking modifications.",
        phone: "+918035317445",
        useCases: ["Reservations", "Room inquiries", "Booking changes", "Amenity information"],
    },
    {
        name: "Feedback Collection Agent",
        category: "all",
        tags: ["Feedback", "English + Hindi"],
        description: "Collects customer feedback through structured surveys with natural conversation flow and sentiment analysis.",
        phone: "+918035317444",
        useCases: ["NPS surveys", "Product feedback", "Service ratings", "Customer insights"],
    },
    {
        name: "Insurance Agent",
        category: "bfsi",
        tags: ["Insurance", "Hindi"],
        description: "Explains insurance products, collects lead information, and schedules appointments with human agents.",
        phone: "+918035317442",
        useCases: ["Product explanation", "Quote generation", "Claim status", "Policy renewal"],
    },
    {
        name: "Education Counselor",
        category: "edtech",
        tags: ["Education", "English"],
        description: "Guides students through course selection, answers queries about programs, and helps with enrollment.",
        phone: "+918035317440",
        useCases: ["Course guidance", "Admission queries", "Fee information", "Enrollment support"],
    },
];

export default function AgentsPage() {
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
                    PRE-BUILT AGENTS
                </span>
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                    Agents That Do More Than Talk
                </h1>
                <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                    Create AI voice agents for India that sound natural, understand context,
                    and speak multiple Indian languages including Hindi, Tamil, Telugu, Bengali, Marathi, Hinglish.
                </p>
            </section>

            {/* Category Tabs */}
            <section className="px-6 pb-8">
                <div className="max-w-6xl mx-auto">
                    <div className="flex flex-wrap justify-center gap-3">
                        {categories.map((cat, idx) => (
                            <button
                                key={cat.id}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${idx === 0
                                        ? "bg-cyan-500 text-black"
                                        : "bg-white/5 text-gray-300 hover:bg-white/10"
                                    }`}
                            >
                                {cat.label}
                                <span className="ml-2 text-xs opacity-60">({cat.count})</span>
                            </button>
                        ))}
                    </div>
                </div>
            </section>

            {/* Agents Grid */}
            <section className="py-12 px-6">
                <div className="max-w-6xl mx-auto grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {agents.map((agent) => (
                        <div
                            key={agent.name}
                            className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-cyan-500/30 transition-all group"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold mb-2 group-hover:text-cyan-400 transition-colors">
                                        {agent.name}
                                    </h3>
                                    <div className="flex flex-wrap gap-2">
                                        {agent.tags.map((tag) => (
                                            <span
                                                key={tag}
                                                className="px-2 py-0.5 bg-white/10 rounded text-xs text-gray-400"
                                            >
                                                {tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button className="w-10 h-10 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center hover:bg-cyan-500/30 transition-colors">
                                        <Play className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            <p className="text-sm text-gray-400 mb-4 line-clamp-2">{agent.description}</p>

                            <div className="flex items-center gap-2 text-cyan-400 text-sm mb-4">
                                <Phone className="w-4 h-4" />
                                {agent.phone}
                            </div>

                            <div className="pt-4 border-t border-white/10">
                                <p className="text-xs text-gray-500 mb-2">Use cases:</p>
                                <div className="flex flex-wrap gap-1">
                                    {agent.useCases.slice(0, 3).map((uc) => (
                                        <span key={uc} className="text-xs text-gray-500">• {uc}</span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA */}
            <section className="py-20 px-6 text-center">
                <h2 className="text-2xl font-bold mb-4">Can't find what you need?</h2>
                <p className="text-gray-400 mb-8">
                    Build custom agents from scratch or work with our team to create specialized solutions.
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                    <Link
                        href="/dashboard/agents"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg"
                    >
                        Build Custom Agent
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                    <Link
                        href="/signup"
                        className="inline-flex items-center gap-2 px-6 py-3 border border-white/20 hover:bg-white/5 rounded-lg"
                    >
                        Talk to Sales
                    </Link>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-8 px-6 border-t border-white/10 text-center text-sm text-gray-500">
                <p>© 2025 Sunona Inc. All Rights Reserved.</p>
            </footer>
        </div>
    );
}
