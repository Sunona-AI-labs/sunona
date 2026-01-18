/**
 * Case Studies Page - Sunona Style
 * Customer success stories with metrics
 */

import Link from "next/link";
import { ArrowRight, ExternalLink, Quote } from "lucide-react";

const caseStudies = [
    {
        company: "Awign",
        logo: "👥",
        industry: "Staffing & Gig Economy",
        headline: "Automated Technical Screening at Scale",
        description: "Awign automated technical screening with Sunona's Voice AI - faster interviews, structured insights, and lower costs at scale. The AI agents conduct initial screening calls, ask standardized questions, and provide structured feedback to recruiters.",
        quote: "Sunona's Voice AI has transformed our hiring process. We can now screen thousands of candidates daily with consistent quality.",
        quoteAuthor: "Head of Talent Acquisition, Awign",
        stats: [
            { value: "17.1", label: "Mins", description: "Longest Interview Duration" },
            { value: "6.8", label: "Mins", description: "Average Interview Duration" },
            { value: "10,000+", label: "", description: "Candidates Screened Monthly" },
            { value: "40%", label: "", description: "Reduction in Time-to-Hire" },
        ],
        challenges: [
            "High volume of applicants requiring manual screening",
            "Inconsistent interview quality across recruiters",
            "Limited availability for after-hours screening",
        ],
        solutions: [
            "24/7 AI-powered initial screening calls",
            "Standardized question set with scoring rubric",
            "Automated scheduling for qualified candidates",
        ],
    },
    {
        company: "Hyreo",
        logo: "🎯",
        industry: "HR Tech",
        headline: "Improved Candidate Experience & Reduced Drop-offs",
        description: "Hyreo improved candidate experience and reduced offer drop-offs with Sunona's 24x7 AI helpline and proactive escalations. The always-on support ensures candidates get instant answers to their queries.",
        quote: "Our offer acceptance rate improved significantly after implementing Sunona's proactive candidate engagement calls.",
        quoteAuthor: "CEO, Hyreo",
        stats: [
            { value: "96.55%", label: "", description: "Call Minutes Growth Rate" },
            { value: "10,000+", label: "", description: "Voice AI Call Conversations" },
            { value: "35%", label: "", description: "Reduction in Offer Drop-offs" },
            { value: "24/7", label: "", description: "Candidate Support Availability" },
        ],
        challenges: [
            "High offer drop-off rates due to delayed communication",
            "Limited bandwidth for personalized candidate outreach",
            "Inconsistent follow-up across hiring pipelines",
        ],
        solutions: [
            "Proactive offer-stage engagement calls",
            "24/7 AI helpline for candidate queries",
            "Automated escalation for complex issues",
        ],
    },
    {
        company: "GoKwik",
        logo: "🛒",
        industry: "E-commerce Tech",
        headline: "Scaled High-Volume E-commerce Conversations",
        description: "GoKwik scaled high-volume e-commerce conversations - cart recovery, surveys, collections - while answering real questions and sharing WhatsApp links for seamless customer experience.",
        quote: "Sunona helped us achieve ROI within the first month. The cart recovery calls alone paid for the entire platform.",
        quoteAuthor: "VP of Operations, GoKwik",
        stats: [
            { value: "4,00,000+", label: "", description: "Unique Engagements" },
            { value: "250+", label: "", description: "Peak Concurrent Calls" },
            { value: "15%", label: "", description: "Cart Recovery Rate" },
            { value: "3x", label: "", description: "ROI in First Month" },
        ],
        challenges: [
            "High cart abandonment rates",
            "Manual follow-up calls not scalable",
            "Peak season call volume spikes",
        ],
        solutions: [
            "Automated cart abandonment calls with offers",
            "Intelligent retry logic for unanswered calls",
            "Scalable infrastructure for peak volumes",
        ],
    },
];

export default function CaseStudiesPage() {
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
                    CASE STUDIES
                </span>
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                    Helping Companies Scale their Call Operations
                </h1>
                <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                    Explore how top organisations leverage Sunona's Voice Agents to Streamline Internal
                    Workflows, Improve Efficiency, and stay competitive in the age of AI.
                </p>
            </section>

            {/* Case Studies */}
            {caseStudies.map((study, idx) => (
                <section
                    key={study.company}
                    className={`py-20 px-6 ${idx % 2 === 0 ? "bg-white/[0.02]" : ""}`}
                >
                    <div className="max-w-5xl mx-auto">
                        {/* Header */}
                        <div className="flex items-center gap-4 mb-8">
                            <span className="text-4xl">{study.logo}</span>
                            <div>
                                <h2 className="text-2xl font-bold">{study.company}</h2>
                                <span className="text-sm text-cyan-400">{study.industry}</span>
                            </div>
                        </div>

                        <h3 className="text-3xl font-bold mb-4">{study.headline}</h3>
                        <p className="text-lg text-gray-400 mb-8">{study.description}</p>

                        {/* Stats Grid */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
                            {study.stats.map((stat) => (
                                <div key={stat.description} className="bg-white/5 rounded-xl p-6 text-center">
                                    <p className="text-3xl font-bold text-white">
                                        {stat.value}
                                        <span className="text-lg text-gray-400">{stat.label}</span>
                                    </p>
                                    <p className="text-sm text-gray-500 mt-2">{stat.description}</p>
                                </div>
                            ))}
                        </div>

                        {/* Quote */}
                        <div className="bg-gradient-to-r from-cyan-500/10 to-transparent border-l-4 border-cyan-500 p-6 rounded-r-xl mb-12">
                            <Quote className="w-8 h-8 text-cyan-500 mb-4" />
                            <p className="text-lg italic text-gray-300 mb-4">"{study.quote}"</p>
                            <p className="text-sm text-gray-500">— {study.quoteAuthor}</p>
                        </div>

                        {/* Challenges & Solutions */}
                        <div className="grid md:grid-cols-2 gap-8">
                            <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-6">
                                <h4 className="font-semibold text-red-400 mb-4">Challenges</h4>
                                <ul className="space-y-3">
                                    {study.challenges.map((c) => (
                                        <li key={c} className="flex items-start gap-3 text-sm text-gray-400">
                                            <span className="text-red-400">✕</span>
                                            {c}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="bg-green-500/5 border border-green-500/20 rounded-xl p-6">
                                <h4 className="font-semibold text-green-400 mb-4">Solutions</h4>
                                <ul className="space-y-3">
                                    {study.solutions.map((s) => (
                                        <li key={s} className="flex items-start gap-3 text-sm text-gray-400">
                                            <span className="text-green-400">✓</span>
                                            {s}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                </section>
            ))}

            {/* CTA */}
            <section className="py-20 px-6 text-center bg-gradient-to-t from-cyan-500/5 to-transparent">
                <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Call Operations?</h2>
                <p className="text-gray-400 mb-8">
                    Join hundreds of companies using Sunona to scale their voice operations.
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                    <Link
                        href="/signup"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg"
                    >
                        Start Free Trial
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                    <Link
                        href="/"
                        className="inline-flex items-center gap-2 px-6 py-3 border border-white/20 hover:bg-white/5 rounded-lg"
                    >
                        Schedule a Demo
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
