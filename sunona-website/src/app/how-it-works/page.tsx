/**
 * How It Works Page - Sunona Style
 * Step-by-step guide with code examples
 */

import Link from "next/link";
import { ArrowRight, Code2, MousePointer, Zap } from "lucide-react";

const steps = [
    {
        number: 1,
        title: "Connect Account",
        subtitle: "STEP ONE",
        description: "Sign in to the Dashboard with your email or OAuth. Get $5 free credits instantly to start testing.",
        color: "amber",
        icon: "🔐",
    },
    {
        number: 2,
        title: "Configure Agent",
        subtitle: "STEP TWO",
        description: "Choose a pre-built template or build from scratch. Configure voice, language, prompts, and integrations.",
        color: "purple",
        icon: "⚙️",
    },
    {
        number: 3,
        title: "Click to Call",
        subtitle: "STEP THREE",
        description: "Trigger calls, campaigns or connect agent with your phone number. Go live in minutes, not weeks.",
        color: "pink",
        icon: "📞",
    },
];

const codeExamples = {
    python: `import requests

url = "https://api.sunona.ai/call"

payload = {
    "agent_id": "12e4567-e89b-12d3-a456-426655440000",
    "recipient_phone_number": "+918123456789",
    "from_phone_number": "+918876543007",
    "user_data": {
        "customer_name": "John Doe",
        "order_id": "ORD-12345",
        "product": "Premium Subscription"
    }
}

headers = {
    "Authorization": "Bearer <your_api_key>",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print(response.json())`,
    javascript: `const options = {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer <your_api_key>',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    agent_id: '12e4567-e89b-12d3-a456-426655440000',
    recipient_phone_number: '+918123456789',
    from_phone_number: '+918876543007',
    user_data: {
      customer_name: 'John Doe',
      order_id: 'ORD-12345',
      product: 'Premium Subscription'
    }
  })
};

fetch('https://api.sunona.ai/call', options)
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));`,
    curl: `curl -X POST https://api.sunona.ai/call \\
  -H "Authorization: Bearer <your_api_key>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "agent_id": "12e4567-e89b-12d3-a456-426655440000",
    "recipient_phone_number": "+918123456789",
    "from_phone_number": "+918876543007",
    "user_data": {
      "customer_name": "John Doe",
      "order_id": "ORD-12345",
      "product": "Premium Subscription"
    }
  }'`,
};

const approaches = [
    {
        icon: <MousePointer className="w-6 h-6" />,
        title: "NO-CODE PLAYGROUND",
        description: "Build and test agents visually without writing any code. Perfect for non-technical users.",
        features: ["Drag-and-drop builder", "Visual flow editor", "One-click deployment", "Real-time testing"],
    },
    {
        icon: <Code2 className="w-6 h-6" />,
        title: "DEVELOPER APIs",
        description: "Full programmatic control with RESTful APIs. Build custom integrations and automate everything.",
        features: ["RESTful API", "Webhooks", "SDKs (Python, JS)", "OpenAPI spec"],
    },
];

export default function HowItWorksPage() {
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
            <section className="py-20 px-6">
                <div className="max-w-6xl mx-auto">
                    <span className="inline-block px-4 py-1 bg-white/5 border border-white/10 rounded-full text-gray-400 text-sm font-medium mb-4">
                        HOW IT WORKS
                    </span>

                    <div className="grid md:grid-cols-2 gap-12 items-center">
                        <div>
                            <h1 className="text-4xl md:text-5xl font-bold mb-4">
                                Power for Devs<br />
                                <span className="text-gray-500">Simplicity for All</span>
                            </h1>
                            <p className="text-xl text-gray-400">
                                Whether you're a no-code builder or a developer, Sunona makes it easy to create
                                powerful conversational voice AI agents that understand Indian languages and accents.
                                Build and scale multilingual voice bots with clicks or code.
                            </p>
                        </div>

                        {/* Approaches */}
                        <div className="space-y-6">
                            {approaches.map((approach) => (
                                <div
                                    key={approach.title}
                                    className="bg-white/5 border border-white/10 rounded-xl p-6 hover:border-cyan-500/30 transition-colors"
                                >
                                    <div className="flex items-center gap-3 mb-3">
                                        <div className="text-cyan-400">{approach.icon}</div>
                                        <h3 className="font-semibold">{approach.title} ↗</h3>
                                    </div>
                                    <p className="text-sm text-gray-400 mb-4">{approach.description}</p>
                                    <div className="flex flex-wrap gap-2">
                                        {approach.features.map((f) => (
                                            <span key={f} className="px-2 py-1 bg-white/5 rounded text-xs text-gray-400">
                                                {f}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </section>

            {/* Steps Section */}
            <section className="py-20 px-6 bg-gradient-to-b from-transparent to-white/5">
                <div className="max-w-6xl mx-auto">
                    <div className="grid md:grid-cols-2 gap-16">
                        {/* Left: Steps */}
                        <div className="space-y-0">
                            {steps.map((step, idx) => {
                                const colors = {
                                    amber: { bg: "bg-amber-500/10", border: "border-amber-500/30", text: "text-amber-400", line: "border-amber-500" },
                                    purple: { bg: "bg-purple-500/10", border: "border-purple-500/30", text: "text-purple-400", line: "border-purple-500" },
                                    pink: { bg: "bg-pink-500/10", border: "border-pink-500/30", text: "text-pink-400", line: "border-pink-500" },
                                };
                                const c = colors[step.color as keyof typeof colors];

                                return (
                                    <div key={step.number} className="relative">
                                        {/* Connector Line */}
                                        {idx < steps.length - 1 && (
                                            <div className={`absolute left-6 top-20 w-0.5 h-16 ${c.line} border-l-2`} />
                                        )}

                                        <div className="flex gap-6 pb-8">
                                            {/* Number Circle */}
                                            <div className={`w-12 h-12 rounded-full ${c.bg} ${c.border} border-2 flex items-center justify-center ${c.text} font-bold text-lg flex-shrink-0`}>
                                                {step.number}
                                            </div>

                                            {/* Content */}
                                            <div className={`${c.bg} ${c.border} border rounded-xl p-6 flex-1`}>
                                                <span className={`text-xs ${c.text} uppercase tracking-wider`}>{step.subtitle}</span>
                                                <h3 className="text-xl font-semibold mt-1 mb-2">{step.title}</h3>
                                                <p className="text-sm text-gray-400">{step.description}</p>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Right: Code Example */}
                        <div className="bg-[#1a1a2e] rounded-xl border border-white/10 overflow-hidden">
                            <div className="flex items-center gap-4 px-4 py-3 border-b border-white/10 bg-white/5">
                                <div className="flex gap-1.5">
                                    <div className="w-3 h-3 rounded-full bg-red-500" />
                                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                                    <div className="w-3 h-3 rounded-full bg-green-500" />
                                </div>
                                <span className="text-xs text-gray-500">API-integration</span>
                                <div className="flex gap-2 ml-auto">
                                    <button className="px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded text-xs">Python</button>
                                    <button className="px-3 py-1 text-gray-500 hover:text-gray-300 text-xs">JavaScript</button>
                                    <button className="px-3 py-1 text-gray-500 hover:text-gray-300 text-xs">cURL</button>
                                </div>
                            </div>
                            <pre className="p-4 text-sm text-gray-300 overflow-x-auto max-h-[500px]">
                                <code>{codeExamples.python}</code>
                            </pre>
                        </div>
                    </div>
                </div>
            </section>

            {/* Quick Start */}
            <section className="py-20 px-6">
                <div className="max-w-4xl mx-auto text-center">
                    <h2 className="text-3xl font-bold mb-4">Get Started in 5 Minutes</h2>
                    <p className="text-gray-400 mb-12">
                        Follow our quickstart guide to make your first AI call
                    </p>

                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="bg-white/5 border border-white/10 rounded-xl p-6 text-left">
                            <Zap className="w-8 h-8 text-cyan-400 mb-4" />
                            <h3 className="font-semibold mb-2">1. Create Account</h3>
                            <p className="text-sm text-gray-400">Sign up and get $5 free credits instantly</p>
                        </div>
                        <div className="bg-white/5 border border-white/10 rounded-xl p-6 text-left">
                            <Code2 className="w-8 h-8 text-cyan-400 mb-4" />
                            <h3 className="font-semibold mb-2">2. Get API Key</h3>
                            <p className="text-sm text-gray-400">Generate your API key from the dashboard</p>
                        </div>
                        <div className="bg-white/5 border border-white/10 rounded-xl p-6 text-left">
                            <ArrowRight className="w-8 h-8 text-cyan-400 mb-4" />
                            <h3 className="font-semibold mb-2">3. Make First Call</h3>
                            <p className="text-sm text-gray-400">Use our API to trigger your first AI call</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="py-20 px-6 text-center bg-gradient-to-t from-cyan-500/5 to-transparent">
                <h2 className="text-3xl font-bold mb-4">Ready to Build?</h2>
                <p className="text-gray-400 mb-8">
                    Start building voice agents today with our free tier
                </p>
                <div className="flex flex-wrap justify-center gap-4">
                    <Link
                        href="/signup"
                        className="inline-flex items-center gap-2 px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg"
                    >
                        Start Free
                        <ArrowRight className="w-4 h-4" />
                    </Link>
                    <Link
                        href="/docs"
                        className="inline-flex items-center gap-2 px-6 py-3 border border-white/20 hover:bg-white/5 rounded-lg"
                    >
                        Read Documentation
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
