/**
 * Contact Page
 * Contact form and support information
 */
"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
    Mail,
    MessageSquare,
    Phone,
    MapPin,
    Send,
    Loader2,
    CheckCircle2,
    Twitter,
    Linkedin,
    Github,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const contactSchema = z.object({
    name: z.string().min(2, "Name is required"),
    email: z.string().email("Please enter a valid email"),
    company: z.string().optional(),
    subject: z.string().min(5, "Subject is required"),
    message: z.string().min(20, "Message must be at least 20 characters"),
});

type ContactFormData = z.infer<typeof contactSchema>;

export default function ContactPage() {
    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const [isSubmitted, setIsSubmitted] = React.useState(false);

    const {
        register,
        handleSubmit,
        formState: { errors },
        reset,
    } = useForm<ContactFormData>({
        resolver: zodResolver(contactSchema),
    });

    const onSubmit = async (data: ContactFormData) => {
        setIsSubmitting(true);
        // Simulate API call
        await new Promise((resolve) => setTimeout(resolve, 1500));
        setIsSubmitting(false);
        setIsSubmitted(true);
        reset();
    };

    return (
        <div className="min-h-screen bg-[#0F0F1A] pt-24 pb-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Hero */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <Badge variant="purple" className="mb-4">
                        Get in Touch
                    </Badge>
                    <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4">
                        Contact Us
                    </h1>
                    <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                        Have questions about Sunona? We&apos;d love to hear from you.
                        Our team is here to help.
                    </p>
                </motion.div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    {/* Contact Form */}
                    <div className="lg:col-span-2">
                        <Card variant="default">
                            <CardContent className="p-8">
                                {isSubmitted ? (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        className="text-center py-12"
                                    >
                                        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-500/10 mb-6">
                                            <CheckCircle2 className="h-8 w-8 text-emerald-400" />
                                        </div>
                                        <h3 className="text-2xl font-bold text-white mb-2">
                                            Message Sent!
                                        </h3>
                                        <p className="text-gray-400 mb-6">
                                            Thank you for reaching out. We&apos;ll get back to you within 24 hours.
                                        </p>
                                        <Button onClick={() => setIsSubmitted(false)}>
                                            Send Another Message
                                        </Button>
                                    </motion.div>
                                ) : (
                                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                            <Input
                                                label="Name"
                                                placeholder="John Doe"
                                                error={errors.name?.message}
                                                {...register("name")}
                                            />
                                            <Input
                                                label="Email"
                                                type="email"
                                                placeholder="john@company.com"
                                                error={errors.email?.message}
                                                {...register("email")}
                                            />
                                        </div>

                                        <Input
                                            label="Company (Optional)"
                                            placeholder="Your company name"
                                            {...register("company")}
                                        />

                                        <Input
                                            label="Subject"
                                            placeholder="How can we help?"
                                            error={errors.subject?.message}
                                            {...register("subject")}
                                        />

                                        <div>
                                            <label className="block text-sm font-medium text-gray-300 mb-2">
                                                Message
                                            </label>
                                            <textarea
                                                placeholder="Tell us more about your needs..."
                                                rows={6}
                                                className={`w-full rounded-lg border bg-[#1A1A2E] px-4 py-3 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-purple-500/20 ${errors.message
                                                        ? "border-red-500 focus:border-red-500"
                                                        : "border-[#374151] focus:border-purple-500"
                                                    }`}
                                                {...register("message")}
                                            />
                                            {errors.message && (
                                                <p className="mt-1 text-sm text-red-400">{errors.message.message}</p>
                                            )}
                                        </div>

                                        <Button
                                            type="submit"
                                            className="w-full sm:w-auto"
                                            disabled={isSubmitting}
                                        >
                                            {isSubmitting ? (
                                                <>
                                                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                                    Sending...
                                                </>
                                            ) : (
                                                <>
                                                    <Send className="h-4 w-4 mr-2" />
                                                    Send Message
                                                </>
                                            )}
                                        </Button>
                                    </form>
                                )}
                            </CardContent>
                        </Card>
                    </div>

                    {/* Contact Info */}
                    <div className="space-y-6">
                        <Card variant="bordered">
                            <CardContent className="p-6">
                                <h3 className="font-semibold text-white mb-4">Contact Information</h3>
                                <div className="space-y-4">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-purple-500/10">
                                            <Mail className="h-5 w-5 text-purple-400" />
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-400">Email</p>
                                            <a href="mailto:hello@sunona.ai" className="text-white hover:text-purple-400">
                                                hello@sunona.ai
                                            </a>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-blue-500/10">
                                            <Phone className="h-5 w-5 text-blue-400" />
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-400">Phone</p>
                                            <a href="tel:+1-555-123-4567" className="text-white hover:text-purple-400">
                                                +1 (555) 123-4567
                                            </a>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 rounded-lg bg-emerald-500/10">
                                            <MapPin className="h-5 w-5 text-emerald-400" />
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-400">Office</p>
                                            <p className="text-white">San Francisco, CA</p>
                                        </div>
                                    </div>
                                </div>
                            </CardContent>
                        </Card>

                        <Card variant="bordered">
                            <CardContent className="p-6">
                                <h3 className="font-semibold text-white mb-4">Support Options</h3>
                                <div className="space-y-3">
                                    <a
                                        href="/docs"
                                        className="flex items-center gap-3 p-3 rounded-lg bg-[#1A1A2E] hover:bg-[#252540] transition-colors"
                                    >
                                        <MessageSquare className="h-5 w-5 text-purple-400" />
                                        <span className="text-gray-300">Documentation</span>
                                    </a>
                                    <a
                                        href="#"
                                        className="flex items-center gap-3 p-3 rounded-lg bg-[#1A1A2E] hover:bg-[#252540] transition-colors"
                                    >
                                        <Github className="h-5 w-5 text-gray-400" />
                                        <span className="text-gray-300">GitHub Issues</span>
                                    </a>
                                </div>
                            </CardContent>
                        </Card>

                        <Card variant="bordered">
                            <CardContent className="p-6">
                                <h3 className="font-semibold text-white mb-4">Follow Us</h3>
                                <div className="flex gap-3">
                                    <a
                                        href="#"
                                        className="p-3 rounded-lg bg-[#1A1A2E] hover:bg-[#252540] transition-colors"
                                    >
                                        <Twitter className="h-5 w-5 text-gray-400 hover:text-blue-400" />
                                    </a>
                                    <a
                                        href="#"
                                        className="p-3 rounded-lg bg-[#1A1A2E] hover:bg-[#252540] transition-colors"
                                    >
                                        <Linkedin className="h-5 w-5 text-gray-400 hover:text-blue-400" />
                                    </a>
                                    <a
                                        href="#"
                                        className="p-3 rounded-lg bg-[#1A1A2E] hover:bg-[#252540] transition-colors"
                                    >
                                        <Github className="h-5 w-5 text-gray-400 hover:text-white" />
                                    </a>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
}
