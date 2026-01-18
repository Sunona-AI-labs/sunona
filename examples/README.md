# Sunona Voice AI - Examples

This folder contains ready-to-run example assistants demonstrating Sunona's capabilities.

---

## 📁 Available Examples

### Voice Assistants
| File | Type | Description |
|------|------|-------------|
| `simple_assistant.py` | 🎤 Full Voice | Complete hands-free voice assistant with mic input |
| `voice_assistant.py` | ⌨️ + 🔊 | Text input with voice output (type to chat) |
| `text_only_assistant.py` | ⌨️ Text | Pure text chat, no audio required |
| `domain_expert.py` | 🧠 Expert | Domain-specific expert assistant |

### Telephony Call Servers
| File | Provider | Port | Description |
|------|----------|------|-------------|
| `twilio_call_server.py` | Twilio | 8001 | Production Twilio call handler |
| `plivo_call_server.py` | Plivo | 8002 | Plivo call handler |
| `vonage_call_server.py` | Vonage | 8003 | Vonage call handler |
| `telnyx_call_server.py` | Telnyx | 8004 | Telnyx call handler |
| `bandwidth_call_server.py` | Bandwidth | 8005 | Bandwidth call handler |

---

## ⚡ Quick Start

### Prerequisites

1. **Install dependencies:**
   ```bash
   pip install sounddevice numpy edge-tts pygame httpx better-profanity langdetect python-dotenv
   ```

2. **Create `.env` file** in the project root with your API keys:
   ```env
   # Required - at least one LLM provider
   OPENROUTER_API_KEY=your_key_here    # Free: https://openrouter.ai/
   GROQ_API_KEY=your_key_here          # Fast: https://console.groq.com/
   
   # Required for voice input (simple_assistant.py only)
   DEEPGRAM_API_KEY=your_key_here      # STT: https://console.deepgram.com/
   
   # Optional - for premium TTS (falls back to free Edge TTS)
   ELEVENLABS_API_KEY=your_key_here    # TTS: https://elevenlabs.io/
   ```

---

## 🎤 1. Simple Assistant (Full Voice)

**Best for:** Hands-free voice conversations, smart speaker experience

**Features:**
- ✅ Voice input (Deepgram STT)
- ✅ Voice output (ElevenLabs/Edge TTS)
- ✅ Barge-in detection (interrupt while speaking)
- ✅ Profanity detection with empathetic responses
- ✅ Multilingual TTS (17 languages)

**Run:**
```bash
python examples/simple_assistant.py
```

**Usage:**
1. Speak naturally - it listens continuously
2. Say "quit", "goodbye", or "bye" to exit
3. Interrupt anytime while it's speaking

**Required keys:** `DEEPGRAM_API_KEY` + (`OPENROUTER_API_KEY` or `GROQ_API_KEY`)

---

## ⌨️🔊 2. Voice Assistant (Text Input + Voice Output)

**Best for:** Chat with voice responses, when you prefer typing

**Features:**
- ✅ Type your messages
- ✅ Voice output (ElevenLabs, else fallback-->Edge TTS)
- ✅ Mute toggle (type "mute" to toggle voice on/off)

**Run:**
```bash
python examples/voice_assistant.py
```

**Usage:**
1. Type your message and press Enter
2. Type "mute" to toggle voice on/off
3. Type "quit" or "bye" to exit

**Required keys:** `OPENROUTER_API_KEY` or `GROQ_API_KEY`

---

## ⌨️ 3. Text Only Assistant (Pure Chat)

**Best for:** Quick text conversations, no audio hardware needed

**Features:**
- ✅ Pure text chat
- ✅ Streaming responses
- ✅ No audio dependencies

**Run:**
```bash
python examples/text_only_assistant.py
```

**Usage:**
1. Type your message and press Enter
2. Type "quit" or "bye" to exit

**Required keys:** `OPENROUTER_API_KEY` or `GROQ_API_KEY`

---

## 🔧 Provider Priority

All examples use this fallback strategy:

| Component | Primary | Fallback |
|-----------|---------|----------|
| **LLM** | OpenRouter (Mistral 7B free) | Groq (Llama 3.1 8B) |
| **TTS** | ElevenLabs (Bella) | Edge TTS (Jenny, free) |
| **STT** | Deepgram (nova-2) | - |

---

## 🆓 Free API Keys

| Service | URL | What you get |
|---------|-----|--------------|
| OpenRouter | https://openrouter.ai/ | Free Mistral 7B access |
| Groq | https://console.groq.com/ | Fast inference, free tier |
| Deepgram | https://console.deepgram.com/ | $200 free credit |
| ElevenLabs | https://elevenlabs.io/ | 10k chars/month free |

---

## 💡 Tips

- **No mic?** Use `voice_assistant.py` or `text_only_assistant.py`
- **Want free TTS?** Don't set `ELEVENLABS_API_KEY` - Edge TTS is unlimited and free
- **Latency issues?** Groq is faster than OpenRouter, set only `GROQ_API_KEY`
- **Backup your work?** Check `backup_simpleassistant.py` for a documented copy

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "No LLM response" | Check your API keys in `.env` |
| Audio not playing | Install pygame: `pip install pygame` |
| Mic not working | Install sounddevice: `pip install sounddevice` |
| TTS error | Falls back to Edge TTS automatically |

---

Made with ❤️ by Sunona AI Team
