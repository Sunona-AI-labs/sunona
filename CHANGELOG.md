# Changelog

All notable changes to the Sunona Voice AI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-01-01

### Fixed

**🛠️ Utility Scripts Robustness**
- Updated `test_api.bat`, `create_agent.bat`, and `make_call.bat` to use `curl.exe` explicitly.
- Prevents conflicts with PowerShell's `curl` alias on Windows.
- Added automatic URL encoding for `+` prefix in `make_call.bat` using a PowerShell helper.

---

## [0.2.0] - 2025-12-31

### Added

**🎙️ ElevenLabs TTS Integration**
- Premium TTS with automatic Edge TTS fallback
- Voice selection via `ELEVENLABS_API_KEY` environment variable
- 8 popular voices mapped (Bella, Rachel, Domi, Elli, Josh, Arnold, Adam, Sam)
- Silent fallback on API errors - no console clutter

**🗣️ Barge-in Detection** (`simple_assistant.py`)
- Monitors microphone during speech playback
- Stops immediately when user starts speaking
- Processes new input without delay
- Configurable speech threshold (3 consecutive chunks)

**💬 LLM Provider Fallback**
- OpenRouter (Mistral 7B free) as primary LLM
- Groq (Llama 3.1 8B) as automatic fallback
- Silent error handling with optional debug output

**🧹 Token Cleaning**
- Added `clean_llm_tokens()` regex helper function
- Removes `<s>`, `</s>`, `[INST]`, `[/INST]`, `<|im_start|>`, `<|im_end|>`
- Applied consistently across all example files

**📝 Documentation**
- Created `examples/README.md` with quick start guides
- Added backup with full documentation (`backup_simpleassistant.py`)
- Enhanced docstrings and type hints

### Changed

- Swapped LLM priority: OpenRouter (free) is now primary, Groq is fallback
- Examples now show which providers are active on startup
- Improved exit word detection (14 phrases supported)
- Console output uses consistent emoji styling

### Fixed

- Token artifacts (`<s>`, etc.) no longer appear in LLM output
- Pygame audio cleanup to prevent file permission errors
- Edge TTS language detection working correctly

---

## [0.1.0] - 2025-12-29

### Initial Release

#### Features

**🎤 Speech-to-Text (11 Providers)**
- Deepgram Nova-2
- Groq Whisper Large V3
- Sarvam Saarika (Indian languages)
- ElevenLabs Scribe
- Gladia Whisper
- Smallest Lightning
- AssemblyAI
- Azure Speech
- AWS Transcribe
- Pixa
- Google Cloud Speech

**🧠 Large Language Models (100+ Models via LiteLLM)**
- OpenRouter (FREE models available)
- OpenAI GPT-4o, GPT-4o-mini
- Anthropic Claude 3.5 Sonnet
- Google Gemini 1.5 Pro
- Groq Llama 3.1
- Mistral Large
- Azure OpenAI

**🔊 Text-to-Speech (10 Providers)**
- ElevenLabs (voice cloning)
- OpenAI TTS
- Deepgram Aura (low latency)
- Cartesia
- Rime
- Smallest
- Sarvam (Indian languages)
- PlayHT
- Azure Speech
- AWS Polly

**📞 Telephony Integration (7 Providers)**
- Twilio
- Plivo
- Exotel
- Vonage
- SignalWire
- Telnyx
- Bandwidth

**🤖 AI Agents (7 Types)**
- ContextualAgent - Deep context tracking
- ExtractionAgent - Lead capture, appointments
- GraphAgent - IVR menus, guided flows
- KnowledgeBaseAgent - RAG-powered FAQ
- WebhookAgent - CRM integration
- SummarizationAgent - Call summaries
- AdaptiveAgent - Dynamic mode switching

**📚 Knowledge Base**
- Universal builder supporting multiple sources
- Website scraping with auto-extraction
- PDF, DOCX, TXT, JSON, CSV support
- Auto-agent generation from knowledge base
- FAQ and product catalog import

**🔄 Smart Call Transfer**
- Intelligent detection of out-of-context queries
- Customer frustration detection
- Seamless handoff to human agents
- Configurable transfer triggers

**💳 Billing System**
- Pay-as-you-go pricing model
- Wallet balance management
- Auto-pay with Stripe integration
- Usage metering for STT, LLM, TTS, Telephony
- Balance warning system (5 levels)
- Email and webhook notifications
- Invoice generation

**🌍 Language Support**
- 20+ languages including:
  - Hindi, Tamil, Telugu, Bengali
  - Kannada, Malayalam, Marathi
  - Gujarati, Punjabi
  - English, Spanish, French, German, etc.

#### Architecture
- Modular pipeline architecture (VAD → STT → LLM → TTS)
- Async/await support throughout
- WebSocket and HTTP/2 support
- Redis integration for state management
- PostgreSQL support for data persistence
- ChromaDB for vector storage

#### Examples
- Text-only assistant
- Simple voice assistant
- Twilio call server with quickstart guide
- Knowledge base builder examples

#### Documentation
- Comprehensive README with feature overview
- Environment variable documentation
- Provider comparison tables
- Cost analysis
- Architecture diagrams
- Quick start guide

### Known Limitations
- Some providers require additional dependencies (marked as optional)
- Docker deployment requires manual configuration
- Limited automated testing coverage

---

## [Unreleased]

### Planned Features
- Additional telephony providers
- More AI agent types
- Enhanced analytics dashboard
- Improved error handling
- Comprehensive test suite
- CI/CD pipeline
