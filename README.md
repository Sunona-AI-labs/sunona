# Sunona Voice AI

<p align="center">
  <strong>🎙️ Enterprise-Grade Voice AI Platform</strong><br>
  Build conversational voice assistants with real-time STT, LLM, and TTS
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/github/stars/Sunona-AI-labs/sunona?style=social" alt="GitHub Stars">
</p>

---

## 🎬 Demo

https://github.com/user-attachments/assets/7f9da85f-72e3-4168-8021-eaf311e6fa3a

> 📞 **This demo showcases Sunona's Twilio integration** — an AI campus recruiter (Priya) making real phone calls with voice conversation.

### 🔧 Required Setup to Replicate This Demo

**1. Environment Variables (`.env`):**

```bash
# LLM (Brain) - Primary: Groq (fastest), Fallback: OpenRouter
GROQ_API_KEY=gsk_xxxxxxxx              # https://console.groq.com/keys
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxx   # https://openrouter.ai/keys (fallback)

# STT (Ears) - https://console.deepgram.com/
DEEPGRAM_API_KEY=xxxxxxxx

# TTS (Voice) - https://elevenlabs.io/app/settings/api-keys
ELEVENLABS_API_KEY=xxxxxxxx

# Telephony - https://www.twilio.com/console
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxx
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
TWILIO_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.app

# Ngrok (for local testing) - https://dashboard.ngrok.com/
NGROK_AUTH_TOKEN=xxxxxxxx
```

**2. Agent Configuration Used:**
- **Config**: [`agent_data/example_recruiter/config_minimal.json`](agent_data/example_recruiter/config_minimal.json)
- **Agent Name**: Priya (Campus Recruiter)
- **Providers**: Deepgram Nova-2 (STT) → LLM → ElevenLabs Turbo (TTS)

**3. Run the Demo (Step-by-Step):**

> 💡 All scripts use **curl** for API testing — no Postman required!

```powershell
# Step 1: Start ngrok tunnel (Terminal 1)
ngrok http 8000

# Step 2: Start Sunona server (Terminal 2)
python -m sunona.server

# Step 3: Health check - verify server is running (Terminal 3)
.\scripts\test_api.bat

# Step 4: View agent details, prompt, users, etc.
.\scripts\view_agent.bat

# Step 5: Create agent - ⚠️ COPY THE UNIQUE agent_id FROM OUTPUT!
.\scripts\create_agent.bat

# Step 6: Make call via Twilio - paste agent_id when prompted
.\scripts\make_call.bat
```

| Step | Script | Purpose |
|------|--------|---------|
| 1 | `ngrok http 8000` | Expose local server to internet |
| 2 | `python -m sunona.server` | Start the Sunona API server |
| 3 | [`test_api.bat`](scripts/test_api.bat) | Health check - verify server connection |
| 4 | [`view_agent.bat`](scripts/view_agent.bat) | View agent config, prompt, and users |
| 5 | [`create_agent.bat`](scripts/create_agent.bat) | Create agent → **copy the `agent_id`** |
| 6 | [`make_call.bat`](scripts/make_call.bat) | Make Twilio call with the agent |

> � See [`scripts/README.md`](scripts/README.md) for detailed script documentation.

---

## ✨ Features at a Glance

| Category | Capabilities |
|----------|--------------|
| **🎤 Speech-to-Text** | 11 providers: Deepgram, Whisper, Groq, AssemblyAI, Azure, Sarvam, ElevenLabs, Gladia, Pixa, Smallest, AWS |
| **🧠 LLM** | 100+ models via LiteLLM: OpenRouter (FREE), OpenAI, Anthropic, Groq, Gemini, Azure, Mistral |
| **🔊 Text-to-Speech** | 11 providers: Edge TTS (FREE), ElevenLabs, OpenAI, Deepgram, Cartesia, Rime, Smallest, Sarvam, PlayHT, Azure, Polly |
| **📞 Telephony** | 7 providers: Twilio, Plivo, Exotel, Vonage, SignalWire, Telnyx, Bandwidth |
| **🤖 AI Agents** | 7 types: Contextual, Extraction, Graph, Knowledge Base, Webhook, Summarization, Adaptive |
| **📚 Knowledge Base** | Universal builder: Website, PDF, DOCX, TXT, JSON, CSV with auto-agent generation |
| **🔄 Smart Transfer** | Intelligent call transfer to humans when AI can't answer |
| **💳 Billing** | Pay-as-you-go, auto-pay, usage metering, balance warnings, non-blocking SMTP notifications |
| **🛡️ Security** | Multi-tenant isolation, O(1) auth lookups, organization-scoped resource gating, secured SSO |
| **⚡ Resilience** | Hardened VAD, circuit breakers for LLM streams, persistent Redis AgentStore, graceful WebSockets |
| **🎙️ WebRTC** | Fully bidirectional browser calling with ultra-low latency audio response feedback |
| **🌍 Languages** | 20+ languages including Hindi, Tamil, Telugu, Bengali (via Sarvam AI) |
| **🛡️ Content Safety** | Multilingual profanity detection (30+ languages) with empathetic responses |

---

## 🚀 Quick Start

### 1. Installation

```powershell
cd sunona

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

### 2. Configure Environment

```powershell
cp .env.example .env
notepad .env  # Add your API keys
```

**Minimum required keys:**
```bash
# LLM (choose one or both)
GROQ_API_KEY=gsk_xxxxxxxx           # Fastest (free tier available)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxx  # FREE models available

# Speech-to-Text
DEEPGRAM_API_KEY=xxxxxxxx

# Text-to-Speech (optional - Edge TTS is FREE and built-in!)
ELEVENLABS_API_KEY=xxxxxxxx
```

### 3. Run Examples

```powershell
# Text-only (LLM only)
python examples/text_only_assistant.py

# 🎙️ Voice assistant (STT + LLM + TTS) - RECOMMENDED
python examples/simple_assistant.py

# Twilio call server (phone calls!)
python examples/twilio_call_server.py
```
### 5. Simple Voice Assistant Features

The `simple_assistant.py` is a complete hands-free voice assistant with:

| Feature | Description |
|---------|-------------|
| **🎤 VAD** | Voice Activity Detection - auto-detects speech |
| **📝 STT** | Deepgram Nova-2 for accurate transcription |
| **🧠 LLM** | Groq (fastest) + OpenRouter fallback |
| **🔊 TTS** | Edge TTS (FREE, unlimited, 17+ languages!) |
| **🌍 Multilingual** | Auto-detects language and speaks in matching voice |
| **💙 Content Safety** | Profanity detection with empathetic responses |
| **⚡ Low Latency** | Optimized for fast, natural conversation |

---

### 4. 🛠️ Quick Start Scripts (Recommended) API ROUTES BASED TESTS(conversational_details.json, config.json, config_minimal.json, users.json)

Use these scripts from the root directory to interact with the Sunona API easily. They handle authentication and URL encoding for you.

**start the python sunona server** : python -m sunona.server 
**dont close this : python -m sunona.server it has intigrated server with twilio server for call services using api's**

| Script | Purpose | Command |
|--------|---------|---------|
| **Health Check** | Verify server connection | `.\scripts\test_api.bat` |
| **Create Agent** | Register a new AI agent | `.\scripts\create_agent.bat` |
| **Make Call** | Initiate a phone call | `.\scripts\make_call.bat` |

> [!TIP]
> These scripts are compatible with both CMD and PowerShell and use `curl.exe` to avoid alias conflicts.


## 🤖 AI Agents

Sunona includes **7 specialized agent types** for different use cases:

### Agent Types

| Agent | Use Case | Key Features |
|-------|----------|--------------|
| **ContextualAgent** | General conversation | Deep context tracking, sentiment awareness, topic management |
| **ExtractionAgent** | Lead capture, appointments | Extracts names, emails, phones, dates with validation |
| **GraphAgent** | IVR menus, guided flows | Node-based flows with conditions and actions |
| **KnowledgeBaseAgent** | FAQ, customer support | RAG-powered answers from your content |
| **WebhookAgent** | CRM integration | Real-time external system integration |
| **SummarizationAgent** | Call summaries | Post-call summaries and action items |
| **AdaptiveAgent** | Dynamic conversations | Auto-switches between modes based on context |

### Smart Agent Selection

```python
from sunona.agents import select_agent

# Auto-select based on use case
agent = select_agent(use_case="lead_capture")

# Auto-detect from first message
agent = select_agent(first_message="I want to book an appointment")

# With knowledge base for FAQ
agent = select_agent(
    use_case="faq",
    knowledge_base=my_knowledge_base,
)
```

---

## 📚 Universal Knowledge Base Builder

Build AI agents from **ANY content source** automatically:

```python
from sunona.knowledge import UniversalKnowledgeBuilder

builder = UniversalKnowledgeBuilder("Acme Corp")

# Add from multiple sources
await builder.add_website("https://acme.com")
builder.add_text("Our hours are 9am-5pm Monday to Friday")
await builder.add_file("products.pdf")
await builder.add_file("faq.docx")
builder.add_faq([
    {"question": "What are your hours?", "answer": "9am-5pm Mon-Fri"}
])

# Build knowledge base
knowledge = builder.build()

# Auto-generate AI agent
agent_config = builder.generate_agent(knowledge, "Acme Assistant")
```

### Supported Sources
| Source | Features |
|--------|----------|
| 🌐 **Website URLs** | Auto-scrapes, extracts contact info, FAQ |
| 📄 **PDF documents** | Text extraction from all pages |
| 📝 **Word documents** | .docx support |
| 📋 **Text files** | .txt support |
| 📊 **JSON files** | Structured data parsing |
| 📈 **CSV files** | Tabular data import |
| ❓ **Direct FAQ** | Question/answer pairs |
| 🛍️ **Product catalogs** | Name, description, pricing |

---

## 🔄 Smart Call Transfer

Seamlessly transfer calls to humans when needed:

```python
from sunona.telephony import create_call_handler, TransferConfig

# Configure transfer
handler = create_call_handler(
    transfer_number="+1234567890",
    knowledge_base=my_knowledge,
    agent_name="John",
)

# Process messages
result = await handler.process_message("What's your refund policy?")

if result["transfer"]:
    # Seamless handoff to human
    print(result["transfer_action"])
```

### Transfer Triggers
| Trigger | When It Happens |
|---------|-----------------|
| 🔄 **Out-of-context** | AI doesn't know the answer (2+ times) |
| 👤 **Customer request** | "Talk to a human", "Get me a manager" |
| ⚠️ **Sensitive topics** | Refunds, complaints, billing issues |
| 😤 **Frustration** | "This is useless", "Not helpful" |
| ⏱️ **Low confidence** | AI confidence drops below threshold |

---

## 💳 Billing System

Complete SaaS billing with **wallet balance, auto-pay, and usage tracking**:

### Pricing

| Service | Rate |
|---------|------|
| **STT** (Deepgram Nova-2) | $0.0145/min |
| **LLM** (GPT-4o-mini) | $0.00015/1K tokens |
| **LLM** (OpenRouter Free) | **FREE** |
| **TTS** (ElevenLabs) | $0.18/1K chars |
| **Telephony** (Twilio) | $0.022/min |
| **Platform Fee** | $0.01/min |

### Balance Warning System

| Balance | Level | Action |
|---------|-------|--------|
| **> $50** | ✅ Healthy | No action |
| **$20-50** | 💡 Moderate | Daily reminder |
| **$10-20** | ⚠️ Low | Warning every 4 hours |
| **$5-10** | 🚨 Critical | Warning every hour |
| **< $5** | ❌ Depleted | **Service blocked** |

### Email & Webhook Notifications

```python
from sunona.billing import send_balance_warning

# Send notification when balance is low
await send_balance_warning(
    account_id="acc_123",
    email="user@example.com",
    balance=15.00,
    warning_level="low",
    webhook_url="https://your-app.com/webhook",
)
```

### Auto-Pay

When auto-pay is enabled and balance drops below threshold:
1. Card is automatically charged
2. Wallet is topped up
3. Email confirmation sent
4. Service continues uninterrupted

---

## 📞 Telephony Integration

### Make Phone Calls with Twilio

```powershell
# Terminal 1: Start ngrok
ngrok http 8000

# Terminal 2: Start server
python examples/twilio_call_server.py

# Terminal 3: Make a call (easiest way)
.\scripts\make_call.bat +917075xxxxxx <agent_id>

# Or via manual POST request (requires URL encoding for +)
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/make-call?to=%2B917075xxxxxx&agent_id=your_id"
```

### Supported Telephony Providers

| Provider | Cost/min | Best For |
|----------|----------|----------|
| **Twilio** | $0.022 | General use, most reliable |
| **Plivo** | $0.015 | Budget option |
| **Exotel** | $0.02 | India-focused |
| **Vonage** | $0.018 | Enterprise |
| **SignalWire** | $0.010 | Cheapest |
| **Telnyx** | $0.012 | Developer-friendly |
| **Bandwidth** | $0.016 | Enterprise |

---

## 🔌 Provider Support

### Speech-to-Text (STT)

| Provider | Model | Cost/min | Languages |
|----------|-------|----------|-----------|
| **Deepgram** | Nova-2 | $0.0145 | 35+ |
| **Groq** | Whisper Large V3 | $0.006 | 100+ |
| **Sarvam** | Saarika | $0.01 | Indian languages |
| **ElevenLabs** | Scribe | $0.015 | 25+ |
| **Gladia** | Whisper | $0.01 | 50+ |
| **Smallest** | Lightning | $0.005 | 10+ |
| **AssemblyAI** | Default | $0.015 | 20+ |
| **Azure** | Speech | $0.016 | 80+ |
| **AWS** | Transcribe | $0.024 | 30+ |

### Large Language Models (LLM)

| Provider | Model | Cost/1K tokens |
|----------|-------|----------------|
| **OpenRouter** | Mistral 7B | **FREE** |
| **OpenRouter** | GPT-4o-mini | $0.00015 |
| **OpenAI** | GPT-4o | $0.005 |
| **Groq** | Llama 3.1 70B | $0.0006 |
| **Anthropic** | Claude 3.5 Sonnet | $0.003 |
| **Google** | Gemini 1.5 Pro | $0.00125 |
| **Mistral** | Mistral Large | $0.002 |
| **Azure** | GPT-4 | $0.006 |

### Text-to-Speech (TTS)

| Provider | Cost/1K chars | Best For |
|----------|---------------|----------|
| **Edge TTS** | **FREE** | Built-in, 17+ languages, unlimited |
| **ElevenLabs** | $0.18 | Highest quality, voice cloning |
| **OpenAI** | $0.015 | Good quality, reliable |
| **Deepgram Aura** | $0.0065 | Low latency |
| **Rime** | $0.10 | Fast, neural |
| **Smallest** | $0.05 | Ultra-cheap |
| **Sarvam** | $0.08 | Indian languages |
| **Cartesia** | $0.10 | Low latency |
| **PlayHT** | $0.15 | Voice cloning |
| **Azure** | $0.016 | Enterprise |
| **AWS Polly** | $0.004 | Cheapest |

---

## 🌍 Indian Language Support

First-class support for Indian languages via **Sarvam AI**:

### Supported Languages
- 🇮🇳 Hindi (hi-IN)
- 🇮🇳 Tamil (ta-IN)
- 🇮🇳 Telugu (te-IN)
- 🇮🇳 Bengali (bn-IN)
- 🇮🇳 Kannada (kn-IN)
- 🇮🇳 Malayalam (ml-IN)
- 🇮🇳 Marathi (mr-IN)
- 🇮🇳 Gujarati (gu-IN)
- 🇮🇳 Punjabi (pa-IN)

### Usage
```python
from sunona.transcriber import create_transcriber
from sunona.synthesizer import create_synthesizer

# Hindi STT
transcriber = create_transcriber("sarvam", language="hi-IN")

# Hindi TTS
synthesizer = create_synthesizer("sarvam", language="hi-IN")
```

---

## 🛡️ Multilingual Content Safety

Detect and handle profanity with **empathy** across **30+ languages**:

### Language Coverage
Supports abuse detection in English, Spanish, French, German, Russian, Italian, Portuguese, Polish, Dutch, Turkish, Japanese, Chinese, Hindi, Arabic, Thai, Vietnamese, Korean, Swedish, Norwegian, Danish, Finnish, Greek, and more.

### How It Works
```python
from better_profanity import profanity

# Automatically loaded
profanity.load_censor_words()

# Detect abuse in ANY language
if profanity.contains_profanity(transcribed_text):
    # Respond with empathy
    response = random_sympathetic_response()  # 10 unique variations
    print(f"🛡️ Content Alert: Abusive language detected")
```

### Features
✅ Detects profanity across 30+ languages simultaneously  
✅ Recognizes contextual variations (f*ck off, fuc*ing, etc.)  
✅ Responds with one of **10 unique sympathetic responses**  
✅ Detailed logging for monitoring and compliance  
✅ Conversation continues respectfully  
✅ No false positives for innocent words (e.g., "assassin")  

### Sympathetic Responses (Sample)
- "I'm sorry you're feeling this way. I'm here to help and support you..."
- "I understand you're upset, and I'm truly sorry about that..."
- "I'm sorry, I can't engage with that kind of language. But I genuinely care..."
- "Hey, I can tell something's really bothering you. I'm sorry you're struggling..."
- "...and 6 more unique empathetic responses"

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SUNONA VOICE AI                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   TWILIO    │  │   PLIVO     │  │   EXOTEL    │  Telephony  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         └────────────────┼────────────────┘                     │
│                          ▼
│  ┌─────────────────────────────────────────────────────────────┐│
│  │            HARDENED CORE (Production Ready)                 ││
│  │  Circuit Breakers │ Graceful Failover │ O(1) Auth Lookups   ││
│  └─────────────────────────────────────────────────────────────┘│
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │            BILLING & MULTI-TENANCY SYSTEM                   ││
│  │  Balance Check → Usage Meter → Tenant Registry → Auto-Pay    ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │            PERSISTENCE & NOTIFICATIONS                      ││
│  │  Redis AgentStore │ aiosmtplib Email │ Webhook Alerts        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 🛡️ Production Hardening (Audit v0.2.0)
The Sunona core has undergone a comprehensive production audit to ensure high reliability:
- **Persistent AgentStore**: Switched from in-memory to a Redis-backed storage layer for enterprise-grade availability and state persistence.
- **Recursive Deadlock Prevention**: Switched to `RLock` for all financial and state transactions.
- **O(1) Authentication**: Hash-indexed API key validation for sub-millisecond overhead.
- **Circuit Breaker Pattern**: Automatic fallback and fail-fast logic for all LLM and STT provider streams.
- **Non-Blocking Notifications**: High-performance SMTP delivery via `aiosmtplib` and async webhooks.
- **Bidirectional WebRTC**: Restored the audio response feedback loop for seamless browser-based voice interactions.

---

## 📁 Project Structure

```
sunona/
├── sunona/                     # Main package
│   ├── agents/                 # 🤖 AI Agents (7 types)
│   │   ├── base_agent.py
│   │   ├── extraction_agent.py
│   │   ├── graph_agent.py
│   │   ├── knowledgebase_agent.py
│   │   ├── webhook_agent.py
│   │   ├── summarization_agent.py
│   │   └── agent_selector.py   # Smart auto-selection
│   ├── llms/                   # 🧠 LLM providers (100+ models)
│   │   └── litellm_llm.py
│   ├── transcriber/            # 🎤 STT providers (11)
│   │   ├── deepgram_transcriber.py
│   │   ├── groq_transcriber.py
│   │   ├── sarvam_transcriber.py
│   │   └── ...
│   ├── synthesizer/            # 🔊 TTS providers (10)
│   │   ├── elevenlabs_synthesizer.py
│   │   ├── rime_synthesizer.py
│   │   ├── sarvam_synthesizer.py
│   │   └── ...
│   ├── telephony/              # 📞 Telephony (7 providers)
│   │   ├── twilio_handler.py
│   │   ├── plivo_handler.py
│   │   └── smart_transfer.py   # Intelligent handoff
│   ├── knowledge/              # 📚 Knowledge Base
│   │   ├── knowledge_builder.py
│   │   └── website_builder.py
│   ├── billing/                # 💳 Billing System
│   │   ├── billing_manager.py
│   │   ├── balance_warning.py  # $20 threshold warnings
│   │   ├── notifications.py    # Email/webhook alerts
│   │   └── middleware.py
│   ├── input_handlers/         # 📥 Audio input
│   ├── output_handlers/        # 📤 Audio output
│   ├── models.py               # Pydantic models
│   ├── constants.py            # Configuration
│   └── providers.py            # Provider registry
├── examples/
│   ├── twilio_call_server.py
│   └── TWILIO_QUICKSTART.md
├── .env.example                # All environment variables
└── requirements.txt
```

---

## ⚙️ Environment Variables

See `.env.example` for all available variables. Key categories:

| Category | Variables |
|----------|-----------|
| **LLM** | OpenRouter, OpenAI, Anthropic, Google, Groq, Azure, Mistral |
| **STT** | Deepgram, AssemblyAI, Sarvam, Gladia, Pixa, Smallest, Azure, AWS |
| **TTS** | ElevenLabs, Rime, Cartesia, PlayHT, Azure, AWS Polly |
| **Telephony** | Twilio, Plivo, Exotel, Vonage, SignalWire, Telnyx, Bandwidth |
| **Database** | PostgreSQL, Redis |
| **Vector Stores** | ChromaDB, Pinecone, Qdrant |
| **Email** | SMTP settings for notifications |
| **Billing** | Stripe integration |

---

## 📊 Cost Comparison

| Feature | Sunona | Competitors |
|---------|--------|-------------|
| Platform Fee | $0.01/min | $0.02-0.05/min |
| Free LLM Options | ✅ OpenRouter | ❌ No |
| Indian Languages | ✅ Sarvam AI | ❌ Limited |
| Smart Transfer | ✅ Included | ❌ Extra cost |
| Knowledge Builder | ✅ Universal | ❌ Basic |
| Auto Agent | ✅ Yes | ❌ No |
| Balance Warnings | ✅ Email + Webhook | ❌ No |
| Auto-Pay | ✅ Yes | ❌ Limited |

**Sunona is 30-50% cheaper with more features!**

---

## 🐳 Docker Deployment

```bash
cd local_setup
docker compose up -d
```

---

## 🤝 Contributing

Contributions welcome! Please open an issue or pull request.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## ⭐ Show Your Love

If you find Sunona useful and it saves you time and money building voice AI, please consider giving us a **star** ⭐ on GitHub!

Your star helps:
- 🚀 Grow the project and community
- 📢 Reach more developers who need voice AI
- 💪 Motivate the team to build amazing features
- 🎯 Attract contributors and partners

**[⭐ Star Sunona on GitHub ⭐](https://github.com/Sunona-AI-labs/sunona)**

It takes just one click and means the world to us! 🙏

<div align="center">

### 📈 GitHub Stars Growth Chart

![Star History Chart](https://api.star-history.com/svg?repos=Sunona-AI-labs/sunona&type=Date)

*Chart auto-updates every 10 minutes!* ⚡

**Last Updated:** January 03, 2026 at 01:03 UTC

**[⭐ Star Sunona on GitHub ⭐](https://github.com/Sunona-AI-labs/sunona)**

</div>

---

<p align="center">
  <strong>Made with ❤️ by the Sunona Team</strong><br>
  <em>Building the future of conversational AI</em>
</p>
