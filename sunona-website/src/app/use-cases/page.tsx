/**
 * Use Cases Page
 * Industry-specific voice AI solutions
 */
"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
    Building2,
    ShoppingBag,
    Stethoscope,
    GraduationCap,
    Plane,
    Home,
    Car,
    Utensils,
    Briefcase,
    HeartPulse,
    Landmark,
    Headphones,
    ArrowRight,
    Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const useCases = [
    {
        id: "real-estate",
        title: "Real Estate",
        description: "Automate property inquiries, schedule viewings, and qualify leads 24/7",
        icon: Home,
        color: "emerald",
        benefits: ["Lead qualification", "Appointment scheduling", "Property info delivery"],
        agents: ["Property Inquiry Agent", "Viewing Scheduler", "Follow-up Agent"],
    },
    {
        id: "healthcare",
        title: "Healthcare",
        description: "Streamline patient scheduling, reminders, and basic health queries",
        icon: HeartPulse,
        color: "red",
        benefits: ["Appointment reminders", "Prescription refills", "Health FAQs"],
        agents: ["Appointment Manager", "Patient Intake", "Reminder Agent"],
    },
    {
        id: "ecommerce",
        title: "E-Commerce",
        description: "Handle order inquiries, returns, and product recommendations",
        icon: ShoppingBag,
        color: "purple",
        benefits: ["Order tracking", "Return processing", "Product suggestions"],
        agents: ["Order Support", "Returns Agent", "Sales Assistant"],
    },
    {
        id: "financial",
        title: "Financial Services",
        description: "Secure account inquiries, payment reminders, and fraud alerts",
        icon: Landmark,
        color: "blue",
        benefits: ["Account balance", "Payment reminders", "Security alerts"],
        agents: ["Account Agent", "Collections Agent", "Fraud Alert Agent"],
    },
    {
        id: "hospitality",
        title: "Hospitality",
        description: "Manage reservations, answer FAQs, and provide concierge services",
        icon: Utensils,
        color: "amber",
        benefits: ["Booking management", "Guest inquiries", "Upselling services"],
        agents: ["Reservation Agent", "Concierge Bot", "Feedback Collector"],
    },
    {
        id: "automotive",
        title: "Automotive",
        description: "Schedule service appointments, handle inquiries, and follow-up leads",
        icon: Car,
        color: "slate",
        benefits: ["Service scheduling", "Test drive booking", "Recall notifications"],
        agents: ["Service Scheduler", "Sales Lead Agent", "Recall Notification"],
    },
    {
        id: "education",
        title: "Education",
        description: "Handle admissions inquiries, schedule tours, and provide info",
        icon: GraduationCap,
        color: "indigo",
        benefits: ["Admissions info", "Tour scheduling", "Course inquiries"],
        agents: ["Admissions Agent", "Tour Scheduler", "Student Support"],
    },
    {
        id: "travel",
        title: "Travel & Airlines",
        description: "Manage bookings, flight changes, and travel advisories",
        icon: Plane,
        color: "cyan",
        benefits: ["Booking changes", "Flight status", "Travel updates"],
        agents: ["Booking Agent", "Flight Status", "Rebooking Assistant"],
    },
    {
        id: "insurance",
        title: "Insurance",
        description: "Quote requests, claims filing, and policy information",
        icon: Building2,
        color: "teal",
        benefits: ["Quote generation", "Claims intake", "Policy queries"],
        agents: ["Quote Agent", "Claims Agent", "Renewal Reminder"],
    },
    {
        id: "recruitment",
        title: "Recruitment",
        description: "Screen candidates, schedule interviews, and collect feedback",
        icon: Briefcase,
        color: "orange",
        benefits: ["Candidate screening", "Interview scheduling", "Status updates"],
        agents: ["Screening Agent", "Interview Scheduler", "Candidate Follow-up"],
    },
    {
        id: "telehealth",
        title: "Telehealth",
        description: "Initial consultations, symptom checking, and appointment booking",
        icon: Stethoscope,
        color: "pink",
        benefits: ["Symptom triage", "Appointment booking", "Follow-up calls"],
        agents: ["Triage Agent", "Appointment Agent", "Check-in Agent"],
    },
    {
        id: "customer-support",
        title: "Customer Support",
        description: "24/7 support for any industry with intelligent routing",
        icon: Headphones,
        color: "violet",
        benefits: ["24/7 availability", "Multi-language", "Smart escalation"],
        agents: ["Tier 1 Support", "Escalation Agent", "Survey Agent"],
    },
];

export default function UseCasesPage() {
    return (
        <div className="min-h-screen bg-[#0F0F1A] pt-24 pb-16">
            {/* Hero */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center mb-16">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <Badge variant="purple" className="mb-4">
                        Industry Solutions
                    </Badge>
                    <h1 className="text-4xl sm:text-5xl font-bold text-white mb-6">
                        Voice AI for Every Industry
                    </h1>
                    <p className="text-xl text-gray-400 max-w-3xl mx-auto mb-8">
                        Pre-built templates and workflows designed for your specific industry.
                        Deploy in minutes, customize as needed.
                    </p>
                    <Link href="/signup">
                        <Button size="lg" rightIcon={<ArrowRight className="h-5 w-5" />}>
                            Start Free Trial
                        </Button>
                    </Link>
                </motion.div>
            </section>

            {/* Use Cases Grid */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {useCases.map((useCase, index) => (
                        <motion.div
                            key={useCase.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.05 }}
                        >
                            <Card variant="default" hover className="h-full">
                                <CardContent className="p-6">
                                    <div className={`inline-flex p-3 rounded-lg bg-${useCase.color}-500/10 mb-4`}>
                                        <useCase.icon className={`h-6 w-6 text-${useCase.color}-400`} />
                                    </div>
                                    <h3 className="text-xl font-bold text-white mb-2">
                                        {useCase.title}
                                    </h3>
                                    <p className="text-gray-400 text-sm mb-4">
                                        {useCase.description}
                                    </p>

                                    {/* Benefits */}
                                    <div className="space-y-2 mb-4">
                                        {useCase.benefits.map((benefit) => (
                                            <div key={benefit} className="flex items-center gap-2 text-sm text-gray-300">
                                                <Check className="h-4 w-4 text-emerald-400 shrink-0" />
                                                {benefit}
                                            </div>
                                        ))}
                                    </div>

                                    {/* Agent Templates */}
                                    <div className="pt-4 border-t border-[#374151]">
                                        <p className="text-xs text-gray-500 mb-2">Available Templates</p>
                                        <div className="flex flex-wrap gap-1">
                                            {useCase.agents.map((agent) => (
                                                <Badge key={agent} variant="outline" size="sm">
                                                    {agent}
                                                </Badge>
                                            ))}
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        </motion.div>
                    ))}
                </div>
            </section>

            {/* CTA Section */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-16">
                <Card variant="elevated" className="bg-gradient-to-r from-purple-900/20 to-blue-900/20">
                    <CardContent className="p-8 sm:p-12 text-center">
                        <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
                            Don&apos;t see your industry?
                        </h2>
                        <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
                            Our platform is fully customizable. Build a custom agent for any use case
                            with our powerful agent builder.
                        </p>
                        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                            <Link href="/dashboard/agents/new">
                                <Button size="lg">
                                    Build Custom Agent
                                </Button>
                            </Link>
                            <Link href="/pricing">
                                <Button variant="outline" size="lg">
                                    View Pricing
                                </Button>
                            </Link>
                        </div>
                    </CardContent>
                </Card>
            </section>
        </div>
    );
}
