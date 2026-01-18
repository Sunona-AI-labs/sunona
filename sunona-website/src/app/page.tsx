/**
 * Homepage - Sunona-Style Marketing Website
 * Dark theme, Voice AI for India, comprehensive landing page
 */

import Link from "next/link";
import { ArrowRight, Play, ExternalLink, Phone, Check } from "lucide-react";

// Trusted Company Logos
const trustedLogos = [
  { name: "GoKwik", logo: "🛒" },
  { name: "FutWork", logo: "💼" },
  { name: "Knot.dating", logo: "💝" },
  { name: "Hypothesis AI", logo: "🧠" },
  { name: "Veera", logo: "🏥" },
  { name: "Classplus", logo: "📚" },
  { name: "Spinny", logo: "🚗" },
  { name: "Awign", logo: "👥" },
  { name: "Hyreo", logo: "🎯" },
];

// Agent Categories
const agentCategories = [
  { id: "all", label: "All Agents" },
  { id: "ecommerce", label: "Ecommerce" },
  { id: "edtech", label: "EdTech" },
  { id: "healthtech", label: "Health Tech" },
  { id: "bfsi", label: "BFSI" },
  { id: "hospitality", label: "Hospitality" },
];

// Agent Templates
const agentTemplates = [
  {
    name: "Customer Support Agent",
    category: "ecommerce",
    tags: ["Customer Support", "English"],
    description: "Provides 24/7 inbound call answering for FAQs and customer triage",
    phone: "+918035317400",
  },
  {
    name: "Cart Abandonment Agent",
    category: "ecommerce",
    tags: ["Cart Abandonment", "English + Hindi"],
    description: "Calls customers with abandoned items in carts, recovering sales",
    phone: "+918035317449",
  },
  {
    name: "COD Confirmation Agent",
    category: "ecommerce",
    tags: ["COD Confirmation", "English + Hindi"],
    description: "Confirms cash-on-delivery orders to reduce RTO rates",
    phone: "+918035317450",
  },
  {
    name: "Recruitment Agent",
    category: "all",
    tags: ["Recruitment", "English"],
    description: "AI agents that screen, interview, and onboard candidates at scale",
    phone: "+918035317441",
  },
  {
    name: "Lead Qualification Agent",
    category: "bfsi",
    tags: ["Lead Qualification", "Hindi"],
    description: "Calls every lead to ask qualifying questions, answer FAQs, and warmly introduce the business",
    phone: "+918035317443",
  },
  {
    name: "Onboarding Agent",
    category: "all",
    tags: ["Onboarding", "English"],
    description: "Conducts personalized guidance calls to warmly onboard users",
    phone: "+918035317448",
  },
];

// Features
const features = [
  {
    icon: "📞",
    title: "Bulk Calling at Scale",
    description: "Run campaigns with thousands of AI calls simultaneously.",
  },
  {
    icon: "⚡",
    title: "Custom API Triggers",
    description: "Call external APIs in real-time during a live conversation.",
  },
  {
    icon: "👤",
    title: "Human-in-the-Loop",
    description: "Transfer call to a real agent instantly when needed.",
  },
  {
    icon: "🔄",
    title: "Workflow Integration",
    description: "Easy to integrate with n8n, Make.com, Zapier, and other tools.",
  },
  {
    icon: "🌍",
    title: "Multilingual",
    description: "Converse fluently in 10+ Indian and Foreign Languages.",
  },
  {
    icon: "💬",
    title: "Natural Conversations",
    description: "Agents understand interruptions, reply with <300ms latency.",
  },
  {
    icon: "🔌",
    title: "Connect Any Model",
    description: "Integrated with 20+ ASR, LLM, and TTS models.",
  },
  {
    icon: "🏢",
    title: "Enterprise Plans",
    description: "Best-in-class pricing and Forward Deployed service.",
  },
  {
    icon: "🔒",
    title: "100% Data Privacy",
    description: "India / USA specific data residency, on-prem deployment.",
  },
  {
    icon: "🎚️",
    title: "Model Switching",
    description: "Run each call with models suited best for your use case.",
  },
];

// Case Studies
const caseStudies = [
  {
    company: "Awign",
    logo: "👥",
    quote: "Awign automated technical screening with Sunona's Voice AI - faster interviews, structured insights, and lower costs at scale.",
    stats: [
      { value: "17.1", label: "Mins", sublabel: "Longest Interview Duration" },
      { value: "6.8", label: "Mins", sublabel: "Average Interview Duration" },
    ],
  },
  {
    company: "Hyreo",
    logo: "🎯",
    quote: "Hyreo improved candidate experience and reduced offer drop-offs with Sunona's 24x7 AI helpline and proactive escalations.",
    stats: [
      { value: "96.55%", label: "", sublabel: "Call minutes growth rate" },
      { value: "10000+", label: "", sublabel: "Voice AI call conversations" },
    ],
  },
  {
    company: "GoKwik",
    logo: "🛒",
    quote: "GoKwik scaled high-volume e-commerce conversations - cart recovery, surveys, collections - while answering real questions and sharing WhatsApp links.",
    stats: [
      { value: "4,00,000+", label: "", sublabel: "Unique engagements" },
      { value: "250+", label: "", sublabel: "Peak concurrent calls" },
    ],
  },
];

// Integration Partners
const integrations = [
  { name: "Twilio", icon: "📱" },
  { name: "OpenAI", icon: "🤖" },
  { name: "Plivo", icon: "☎️" },
  { name: "ElevenLabs", icon: "🎙️" },
  { name: "Deepgram", icon: "👂" },
  { name: "Anthropic", icon: "🧠" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white">
      {/* Announcement Banner */}
      <div className="bg-gradient-to-r from-cyan-500/[0.06] via-transparent to-blue-500/[0.06] border-b border-white/[0.05] py-2 text-center text-[13px]">
        <span className="text-zinc-400">India's most promising startups of 2026 – </span>
        <Link href="#" className="text-cyan-400 hover:text-cyan-300 font-medium transition-colors">
          YourStory Tech30 2025 ↗
        </Link>
      </div>

      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-[#0a0a0f]/95 backdrop-blur-xl border-b border-white/[0.05]">
        <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <span className="text-white font-bold text-sm">S</span>
            </div>
            <span className="text-lg font-bold tracking-tight">SUNONA</span>
          </Link>

          <div className="hidden md:flex items-center gap-7 text-[13px]">
            <Link href="#how-it-works" className="text-zinc-400 hover:text-white transition-colors font-medium">How it Works</Link>
            <Link href="#agents" className="text-zinc-400 hover:text-white transition-colors font-medium">Agents</Link>
            <Link href="#features" className="text-zinc-400 hover:text-white transition-colors font-medium">Features</Link>
            <Link href="#case-studies" className="text-zinc-400 hover:text-white transition-colors font-medium">Case Studies</Link>
            <Link href="/pricing" className="text-zinc-400 hover:text-white transition-colors font-medium">Pricing</Link>
            <Link href="/docs" className="text-zinc-400 hover:text-white transition-colors font-medium">Documentation</Link>
            <Link href="#" className="text-zinc-400 hover:text-white transition-colors font-medium">Careers</Link>
          </div>

          <div className="flex items-center gap-3">
            <Link href="/login" className="px-4 py-2 text-zinc-400 hover:text-white text-[13px] font-medium transition-colors">Login</Link>
            <Link
              href="/signup"
              className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg text-[13px] transition-all shadow-lg shadow-cyan-500/20"
            >
              Book a Demo
            </Link>
          </div>
        </div>
      </nav>


      {/* Hero Section */}
      <section className="relative min-h-[95vh] flex flex-col items-center justify-center pt-24 pb-32 px-6 overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#ffffff05_1px,transparent_1px),linear-gradient(to_bottom,#ffffff05_1px,transparent_1px)] bg-[size:60px_60px]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(34,211,238,0.08)_0%,transparent_60%)]" />
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[900px] h-[600px] bg-cyan-500/[0.07] rounded-full blur-[120px]" />
        <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent" />

        <div className="max-w-5xl w-full flex flex-col items-center text-center relative z-10">
          {/* YC Badge */}
          <div className="inline-flex items-center gap-3 px-5 py-2.5 bg-white/[0.03] border border-white/[0.08] rounded-full mb-12 backdrop-blur-sm hover:border-white/20 transition-colors cursor-default">
            <span className="text-orange-400 text-sm">★</span>
            <span className="text-[13px] text-zinc-400 font-medium">Backed by</span>
            <div className="flex items-center gap-1.5">
              <span className="px-2 py-0.5 bg-orange-500 text-white text-[11px] font-black rounded">Y</span>
              <span className="text-[13px] font-semibold text-white">Combinator</span>
            </div>
          </div>

          <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold mb-8 leading-[1.05] tracking-[-0.02em] text-white">
            Voice AI<br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-400 to-blue-500">
              Built for India
            </span>
          </h1>

          <p className="text-lg md:text-xl text-zinc-400 mb-12 max-w-3xl mx-auto leading-relaxed font-light">
            Powering India's businesses with AI Voice Agents from customer service to recruitment, and everything in between. Handle <span className="text-white font-medium">thousands of calls every minute</span> with natural, multilingual intelligence.
          </p>

          <Link
            href="/signup"
            className="group inline-flex items-center gap-3 px-8 py-4 bg-cyan-500 hover:bg-cyan-400 text-black font-bold rounded-xl transition-all duration-300 shadow-[0_0_40px_rgba(34,211,238,0.25)] hover:shadow-[0_0_60px_rgba(34,211,238,0.35)] hover:scale-[1.02]"
          >
            Experience Sunona
            <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>
      </section>

      {/* Trusted By Section */}
      <section className="py-20 px-6 border-y border-white/[0.06] bg-[#08080c] relative">
        <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/[0.02] to-transparent pointer-events-none" />
        <div className="max-w-7xl mx-auto flex flex-col items-center relative z-10">
          <p className="text-center text-zinc-400 mb-6 text-base font-medium tracking-tight">
            <span className="text-white font-semibold">500+ Companies</span> rely on <span className="text-white font-semibold">Sunona</span> to power their Voice AI Stack
          </p>
          <p className="text-center text-zinc-500 mb-16 text-sm max-w-2xl leading-relaxed">
            Leading the way in <span className="text-cyan-400 font-medium px-2 py-0.5 bg-cyan-400/10 rounded border border-cyan-400/20">10+ vernacular</span> Indian languages including Hinglish, Hindi, Tamil, Telugu, and more.
          </p>

          <div className="flex flex-wrap justify-center gap-x-16 gap-y-10 items-center">
            {trustedLogos.map((company) => (
              <div key={company.name} className="flex flex-col items-center group cursor-default opacity-50 hover:opacity-100 transition-opacity duration-500">
                <span className="text-4xl mb-3 grayscale group-hover:grayscale-0 transition-all duration-500 transform group-hover:scale-110">{company.logo}</span>
                <p className="text-[9px] uppercase tracking-[0.3em] font-bold text-zinc-600 group-hover:text-cyan-400 transition-colors duration-300">{company.name}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Introducing & Our Agents Section */}
      <section className="py-32 px-6 relative overflow-hidden" id="agents">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/40 to-transparent" />
        <div className="absolute -left-60 top-20 w-[400px] h-[400px] bg-blue-500/[0.04] rounded-full blur-[120px]" />
        <div className="absolute right-0 bottom-0 w-[300px] h-[300px] bg-cyan-500/[0.03] rounded-full blur-[100px]" />

        <div className="max-w-7xl mx-auto flex flex-col items-center relative z-10">
          {/* Introducing Banner */}
          <div className="flex flex-col items-center text-center mb-28 max-w-4xl">
            <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-cyan-500/10 border border-cyan-500/20 rounded-full text-cyan-400 text-[11px] font-bold tracking-[0.15em] mb-8 uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              Introducing Sunona
            </span>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-8 leading-[1.08] text-white tracking-tight">
              Seamlessly Build, Test, Deploy, and Scale<br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-400 to-blue-500">
                Conversational Voice AI Agents
              </span>
            </h2>
            <p className="text-lg md:text-xl text-zinc-400 max-w-3xl leading-relaxed font-light">
              Transform your business operations with natural-sounding AI agents.
              Go from initial idea to live production calls in <span className="text-white font-medium">minutes, not weeks</span>.
            </p>
          </div>

          {/* Our Agents Header */}
          <div className="flex flex-col items-center text-center mb-16 max-w-3xl">
            <span className="text-[10px] text-cyan-500 font-bold uppercase tracking-[0.35em] mb-5">Explore the stack</span>
            <h3 className="text-3xl md:text-4xl font-bold text-white mb-6 tracking-tight">Agents That Do More Than Talk</h3>
            <p className="text-zinc-400 leading-relaxed text-lg font-light">
              Create AI voice agents that sound natural, understand context,
              and speak multiple Indian languages including <span className="text-white font-medium">Hindi, Tamil, Telugu, Bengali, Marathi, and Hinglish</span>.
            </p>
          </div>

          {/* Category Tabs - Bolna Pill Style */}
          <div className="flex flex-wrap justify-center gap-3 mb-16">
            {agentCategories.map((cat, idx) => (
              <button
                key={cat.id}
                className={`px-5 py-2.5 rounded-full text-[13px] font-semibold transition-all duration-300 ${idx === 0
                  ? "bg-white text-zinc-900 shadow-lg shadow-white/10"
                  : "bg-white/[0.04] text-zinc-400 border border-white/[0.08] hover:border-white/20 hover:text-white hover:bg-white/[0.08]"
                  }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Agent Cards Grid */}
          <div className="grid md:grid-cols-2 gap-6 w-full max-w-5xl">
            {agentTemplates.map((agent) => (
              <div
                key={agent.name}
                className="group relative bg-[#0f0f15] border border-white/[0.06] rounded-2xl p-7 hover:border-cyan-500/40 transition-all duration-400 hover:-translate-y-0.5"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/[0.04] via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-400 rounded-2xl" />

                <div className="relative z-10">
                  <div className="flex items-start justify-between mb-5">
                    <div className="flex-1">
                      <h4 className="text-lg font-bold text-white mb-2.5 group-hover:text-cyan-400 transition-colors">{agent.name}</h4>
                      <div className="flex flex-wrap gap-1.5">
                        {agent.tags.map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 bg-white/[0.04] border border-white/[0.08] rounded text-[10px] font-semibold uppercase tracking-wider text-zinc-500"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <button className="w-11 h-11 rounded-xl bg-cyan-500 text-black flex items-center justify-center hover:bg-cyan-400 transition-all shadow-lg shadow-cyan-500/25 active:scale-95">
                      <Play className="fill-current w-4 h-4 ml-0.5" />
                    </button>
                  </div>

                  <p className="text-zinc-400 text-sm leading-relaxed mb-6 line-clamp-2">
                    {agent.description}
                  </p>

                  <div className="flex items-center justify-between pt-5 border-t border-white/[0.06]">
                    <div className="flex items-center gap-2.5 text-cyan-400 font-mono text-xs">
                      <div className="w-7 h-7 rounded-full bg-cyan-500/10 flex items-center justify-center">
                        <Phone className="w-3 h-3" />
                      </div>
                      {agent.phone}
                    </div>
                    <button className="text-[10px] text-zinc-500 hover:text-white flex items-center gap-1.5 uppercase tracking-widest font-bold transition-colors">
                      Details <ExternalLink className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-28 px-6 relative" id="how-it-works">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-white/[0.015] to-transparent pointer-events-none" />
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent" />
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="mb-20 flex flex-col items-center">
            <span className="text-[10px] text-zinc-500 uppercase tracking-[0.35em] mb-5">Execution Layer</span>
            <div className="flex flex-col items-center text-center gap-5 max-w-4xl">
              <div>
                <h2 className="text-4xl md:text-5xl font-bold mb-3 text-white tracking-tight">Power for Developers</h2>
                <h2 className="text-4xl md:text-5xl font-bold text-zinc-700 tracking-tight">Simplicity for Business</h2>
              </div>
              <p className="text-zinc-400 text-lg md:text-xl font-light leading-relaxed max-w-2xl">
                Whether you're a no-code builder or an enterprise developer, Sunona makes it easy to create
                powerful conversational voice AI agents.
              </p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-10">
            {/* Left: Steps */}
            <div className="space-y-6">
              <div className="flex items-center gap-3 mb-8">
                <button className="flex items-center gap-2 px-4 py-2 bg-white/[0.06] border border-cyan-500/30 rounded-lg text-sm font-medium text-cyan-400 transition-all">
                  <span className="text-cyan-400">✨</span>
                  NO-CODE PLAYGROUND
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-white/[0.03] border border-white/[0.06] rounded-lg text-sm font-medium text-zinc-500 hover:text-zinc-300 hover:border-white/10 transition-all">
                  DEVELOPER APIs
                </button>
              </div>

              {/* Step 1 */}
              <div className="relative pl-7 border-l-2 border-amber-500/80 pb-6">
                <div className="absolute -left-[11px] top-0 w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center text-black text-[10px] font-bold shadow-lg shadow-amber-500/30">1</div>
                <div className="bg-amber-500/[0.08] border border-amber-500/25 rounded-xl p-5">
                  <p className="text-[10px] text-amber-400 uppercase tracking-[0.2em] mb-1.5 font-bold">Step One</p>
                  <h4 className="text-base font-semibold text-white mb-1">Connect Account</h4>
                  <p className="text-sm text-zinc-400">Sign in to the Dashboard</p>
                </div>
              </div>

              {/* Step 2 */}
              <div className="relative pl-7 border-l-2 border-purple-500/80 pb-6">
                <div className="absolute -left-[11px] top-0 w-5 h-5 bg-purple-500 rounded-full flex items-center justify-center text-white text-[10px] font-bold shadow-lg shadow-purple-500/30">2</div>
                <div className="bg-purple-500/[0.08] border border-purple-500/25 rounded-xl p-5">
                  <p className="text-[10px] text-purple-400 uppercase tracking-[0.2em] mb-1.5 font-bold">Step Two</p>
                  <h4 className="text-base font-semibold text-white mb-1">Configure Agent</h4>
                  <p className="text-sm text-zinc-400">Choose a pre-built template or build from scratch</p>
                </div>
              </div>

              {/* Step 3 */}
              <div className="relative pl-7 border-l-2 border-pink-500/80">
                <div className="absolute -left-[11px] top-0 w-5 h-5 bg-pink-500 rounded-full flex items-center justify-center text-white text-[10px] font-bold shadow-lg shadow-pink-500/30">3</div>
                <div className="bg-pink-500/[0.08] border border-pink-500/25 rounded-xl p-5">
                  <p className="text-[10px] text-pink-400 uppercase tracking-[0.2em] mb-1.5 font-bold">Step Three</p>
                  <h4 className="text-base font-semibold text-white mb-1">Click to Call</h4>
                  <p className="text-sm text-zinc-400">Trigger calls, campaigns or connect agent with your phone number</p>
                </div>
              </div>
            </div>

            {/* Right: Code Preview */}
            <div className="bg-[#0c0c14] rounded-2xl border border-white/[0.06] overflow-hidden shadow-2xl">
              <div className="flex items-center gap-4 px-5 py-3 border-b border-white/[0.06] bg-white/[0.02]">
                <div className="flex gap-1.5">
                  <span className="w-3 h-3 rounded-full bg-red-500/80" />
                  <span className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <span className="w-3 h-3 rounded-full bg-green-500/80" />
                </div>
                <span className="text-[11px] text-zinc-500 font-medium">API-integration</span>
                <div className="flex gap-1.5 ml-auto">
                  <button className="px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded-md text-[11px] font-medium border border-cyan-500/30">Python</button>
                  <button className="px-3 py-1 text-zinc-500 hover:text-zinc-300 text-[11px] hover:bg-white/[0.04] rounded-md transition-colors">JavaScript</button>
                  <button className="px-3 py-1 text-zinc-500 hover:text-zinc-300 text-[11px] hover:bg-white/[0.04] rounded-md transition-colors">cURL</button>
                </div>
              </div>
              <pre className="p-5 text-[13px] text-zinc-300 overflow-x-auto font-mono leading-relaxed">
                <code>{`import requests

url = "https://api.sunona.ai/call"

payload = {
    "agent_id": "12e4567-e89b-12d3-a456...",
    "recipient_phone_number": "+918123456789",
    "from_phone_number": "+918876543007",
    "user_data": {
        "variable1": "value1",
        "variable2": "value2",
    }
}

headers = {
    "Authorization": "Bearer <token>",
    "Content-Type": "application/json"
}

response = requests.request(
    "POST", url, json=payload, headers=headers
)
print(response.text)`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-28 px-6 relative bg-[#08080c]" id="features">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-cyan-500/[0.025] rounded-full blur-[150px] pointer-events-none" />
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="text-center mb-20">
            <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/[0.03] border border-white/[0.08] rounded-full text-zinc-400 text-[11px] font-bold tracking-[0.15em] mb-8 uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              Infrastructure
            </span>
            <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight text-white">
              Features That Power <span className="text-cyan-400">Real</span> Voice Agents
            </h2>
            <p className="text-zinc-400 max-w-2xl mx-auto text-lg font-light leading-relaxed">
              With integrated speech, telephony, and APIs, Sunona equips you with everything
              required to move from idea to live deployment.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="group bg-[#0c0c14] border border-white/[0.05] rounded-2xl p-6 hover:border-cyan-500/30 transition-all duration-300 hover:-translate-y-0.5"
              >
                <div className="w-12 h-12 bg-cyan-500/10 border border-cyan-500/20 rounded-xl flex items-center justify-center text-2xl mb-5 group-hover:scale-105 group-hover:bg-cyan-500/15 transition-all">
                  {feature.icon}
                </div>
                <h4 className="text-sm font-bold text-white mb-2 tracking-tight">{feature.title}</h4>
                <p className="text-[13px] text-zinc-500 leading-relaxed group-hover:text-zinc-400 transition-colors">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Case Studies Section */}
      <section className="py-28 px-6 relative bg-gradient-to-b from-[#08080c] to-cyan-500/[0.02]" id="case-studies">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/[0.03] border border-white/[0.08] rounded-full text-zinc-400 text-[11px] font-bold tracking-[0.15em] mb-8 uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              Proven Success
            </span>
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-6">
              Reliable Call Operations at Scale
            </h2>
            <p className="text-zinc-400 text-lg font-light leading-relaxed max-w-2xl mx-auto">
              Explore how top organisations leverage Sunona's Voice Agents to streamline internal
              workflows and improve efficiency.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {caseStudies.map((study) => (
              <div
                key={study.company}
                className="bg-[#0c0c14] border border-white/[0.05] rounded-2xl p-8 hover:border-cyan-500/25 transition-all duration-400 relative group overflow-hidden"
              >
                <div className="absolute top-0 right-0 w-28 h-28 bg-cyan-500/[0.04] rounded-full -mr-14 -mt-14 blur-2xl group-hover:bg-cyan-500/[0.08] transition-all" />

                <div className="flex items-center gap-4 mb-8 relative z-10">
                  <div className="w-11 h-11 bg-white/[0.04] border border-white/[0.08] rounded-xl flex items-center justify-center text-2xl">
                    {study.logo}
                  </div>
                  <span className="text-lg font-bold tracking-tight text-white">{study.company}</span>
                </div>

                <p className="text-base text-zinc-300 mb-8 leading-relaxed font-light relative z-10">
                  "{study.quote}"
                </p>

                <div className="grid grid-cols-2 gap-6 pt-6 border-t border-white/[0.06] relative z-10">
                  {study.stats.map((stat, idx) => (
                    <div key={idx} className="flex flex-col">
                      <p className="text-2xl font-bold text-white mb-0.5 tracking-tight">
                        {stat.value}
                        <span className="text-cyan-400 text-xs ml-1 font-medium">{stat.label}</span>
                      </p>
                      <p className="text-[9px] text-zinc-500 uppercase tracking-[0.15em] font-bold">
                        {stat.sublabel}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations Section */}
      <section className="py-28 px-6 relative bg-[#08080c]">
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-zinc-800 to-transparent" />
        <div className="absolute top-1/2 right-0 w-80 h-80 bg-blue-500/[0.06] rounded-full blur-[100px] pointer-events-none" />
        <div className="max-w-7xl mx-auto flex flex-col items-center">
          <div className="grid md:grid-cols-2 gap-20 items-center w-full">
            <div className="flex flex-col items-start text-left">
              <span className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/[0.03] border border-white/[0.08] rounded-full text-zinc-400 text-[11px] font-bold tracking-[0.15em] mb-8 uppercase">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                Ecosystem
              </span>
              <h2 className="text-4xl md:text-5xl font-bold mb-6 text-white tracking-tight leading-[1.08]">Seamless<br />Integrations</h2>
              <p className="text-zinc-400 text-lg font-light leading-relaxed mb-10 max-w-md">
                Sunona works hand-in-hand with leading platforms to
                supercharge your communication stack. Easily plug Sunona into
                your infrastructure.
              </p>
              <Link
                href="/docs"
                className="group inline-flex items-center gap-2.5 px-6 py-3 bg-white/[0.04] border border-white/[0.08] text-white rounded-xl text-sm font-semibold hover:bg-white/[0.08] hover:border-cyan-500/30 transition-all"
              >
                Explore all Integrations
                <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>

            <div className="flex justify-center relative">
              <div className="relative w-72 h-72 flex items-center justify-center">
                {/* Orbital Rings */}
                <div className="absolute inset-0 border border-white/[0.04] rounded-full" />
                <div className="absolute inset-10 border border-white/[0.06] rounded-full animate-[spin_25s_linear_infinite]" />
                <div className="absolute inset-20 border border-cyan-500/15 rounded-full animate-[spin_18s_linear_infinite_reverse]" />

                {/* Center Logo */}
                <div className="relative w-20 h-20 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-cyan-500/30 z-10 transition-transform hover:scale-105">
                  <span className="text-white font-black text-2xl">S</span>
                </div>

                {/* Integration Icons */}
                {integrations.map((int, idx) => {
                  const angle = (idx * 360) / integrations.length;
                  const distance = 120;
                  const x = Math.cos((angle - 90) * Math.PI / 180) * distance;
                  const y = Math.sin((angle - 90) * Math.PI / 180) * distance;
                  return (
                    <div
                      key={int.name}
                      className="absolute w-12 h-12 bg-[#0c0c14] border border-white/[0.08] rounded-xl flex items-center justify-center text-xl shadow-lg transition-all hover:border-cyan-500/40 hover:scale-110 z-20 group cursor-default"
                      style={{
                        transform: `translate(${x}px, ${y}px)`,
                      }}
                    >
                      <span className="group-hover:drop-shadow-[0_0_6px_rgba(34,211,238,0.4)]">{int.icon}</span>
                      <div className="absolute -bottom-7 left-1/2 -translate-x-1/2 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity">
                        <span className="text-[8px] uppercase tracking-[0.2em] font-bold text-cyan-400">{int.name}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-28 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[#08080c] via-cyan-500/[0.03] to-cyan-500/[0.06] pointer-events-none" />
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent" />
        <div className="max-w-4xl mx-auto relative z-10 text-center flex flex-col items-center">
          <div className="w-16 h-16 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-2xl flex items-center justify-center shadow-2xl shadow-cyan-500/30 mb-10 transform rotate-6">
            <span className="text-white font-black text-xl">S</span>
          </div>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 tracking-tight text-white leading-[1.08]">
            Ready to Build Smarter<br />Voice Agents?
          </h2>
          <p className="text-zinc-400 text-lg md:text-xl font-light mb-10 max-w-2xl leading-relaxed">
            Connect with our team for a personalized demo and see how Sunona can
            accelerate your journey from idea to live deployment.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="/signup"
              className="px-8 py-4 bg-cyan-500 text-black font-bold rounded-xl hover:bg-cyan-400 transition-all shadow-[0_0_40px_rgba(34,211,238,0.25)] hover:shadow-[0_0_60px_rgba(34,211,238,0.35)] hover:scale-[1.02]"
            >
              Get Started Now
            </Link>
            <Link
              href="/docs"
              className="px-8 py-4 bg-white/[0.04] border border-white/[0.08] text-white font-bold rounded-xl hover:bg-white/[0.08] hover:border-white/15 transition-all"
            >
              Read Documentation
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-14 px-6 border-t border-white/[0.06] bg-[#06060a]">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-10 mb-10">
            {/* Brand */}
            <div>
              <div className="flex items-center gap-2.5 mb-5">
                <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">S</span>
                </div>
                <span className="text-lg font-bold tracking-tight">SUNONA</span>
              </div>
              <div className="flex items-center gap-5 text-zinc-500">
                <Link href="#" className="hover:text-white transition-colors text-sm">𝕏</Link>
                <Link href="#" className="hover:text-white transition-colors text-sm font-semibold">in</Link>
                <Link href="#" className="hover:text-white transition-colors text-sm">▶️</Link>
              </div>
            </div>

            {/* API Documentation */}
            <div>
              <h5 className="font-semibold mb-4 text-sm text-white">API Documentation</h5>
              <ul className="space-y-2.5 text-[13px] text-zinc-400">
                <li><Link href="/docs" className="hover:text-white transition-colors">API authentication</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">Using Agents APIs</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">Making phone calls APIs</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">Get call data APIs</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">Batch APIs</Link></li>
              </ul>
            </div>

            {/* Product */}
            <div>
              <h5 className="font-semibold mb-4 text-sm text-white">Product</h5>
              <ul className="space-y-2.5 text-[13px] text-zinc-400">
                <li><Link href="/dashboard" className="hover:text-white transition-colors">Dashboard</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">Function tool calling</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">PDFs, RAGs & Knowledge bases</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">Using Twilio with Sunona</Link></li>
                <li><Link href="/docs" className="hover:text-white transition-colors">Multilingual support</Link></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h5 className="font-semibold mb-4 text-sm text-white">Company</h5>
              <ul className="space-y-2.5 text-[13px] text-zinc-400">
                <li><Link href="#" className="hover:text-white transition-colors">YC Launch</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Contact us</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Schedule a Call</Link></li>
                <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing & Plans</Link></li>
                <li><Link href="#" className="hover:text-white transition-colors">Sunona Blogs</Link></li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
                  <Link href="#" className="hover:text-white transition-colors">System status</Link>
                </li>
              </ul>
            </div>
          </div>

          <div className="flex flex-col md:flex-row items-center justify-between pt-8 border-t border-white/[0.06] text-[13px] text-zinc-500">
            <p>© 2025 Sunona Inc. All Rights Reserved.</p>
            <div className="flex gap-6 mt-4 md:mt-0">
              <Link href="/terms" className="hover:text-white transition-colors">Terms of Use</Link>
              <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
            </div>
          </div>
        </div>
      </footer>

      {/* Floating Chat Button */}
      <div className="fixed bottom-6 right-6 z-50">
        <button className="flex items-center gap-2 px-4 py-3 bg-cyan-500 text-black font-semibold rounded-full shadow-lg shadow-cyan-500/25 hover:bg-cyan-400 transition-all hover:scale-105">
          <span className="w-5 h-5 bg-black/15 rounded-full flex items-center justify-center text-xs">💬</span>
          Talk to us
        </button>
      </div>
    </div>
  );
}
