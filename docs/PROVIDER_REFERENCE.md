# Sunona Voice AI - Provider Reference

Quick reference for all supported providers and how to configure them.

---

## 🧠 LLM Providers (The "Brain")

| Provider | Model Examples | Env Key | Cost | Notes |
|----------|---------------|---------|------|-------|
| **OpenRouter** | `mistralai/mistral-7b-instruct:free` | `OPENROUTER_API_KEY` | **FREE** | Best for dev |
| **OpenRouter** | `anthropic/claude-3.5-sonnet` | `OPENROUTER_API_KEY` | $0.003/1K | High quality |
| **Groq** | `llama-3.1-70b-versatile` | `GROQ_API_KEY` | $0.0006/1K | Ultra fast |
| **OpenAI** | `gpt-4o-mini` | `OPENAI_API_KEY` | $0.00015/1K | Reliable |
| **OpenAI** | `gpt-4o` | `OPENAI_API_KEY` | $0.005/1K | Best quality |
| **Google** | `gemini-1.5-flash` | `GOOGLE_API_KEY` | $0.00125/1K | Fast |

### Config Example:
```json
"llm_agent": {
  "streaming_model": "openrouter/mistralai/mistral-7b-instruct:free"
}
```

---

## 🔊 TTS Providers (The "Voice")

| Provider | Voice Examples | Env Key | Cost | Notes |
|----------|---------------|---------|------|-------|
| **Edge TTS** | `en-US-JennyNeural`, `en-IN-NeerjaNeural` | None | **FREE** | Unlimited! |
| **ElevenLabs** | `Rachel`, `Adam` | `ELEVENLABS_API_KEY` | $0.18/1K chars | Best quality |
| **OpenAI** | `alloy`, `echo`, `shimmer` | `OPENAI_API_KEY` | $0.015/1K chars | Good quality |
| **Deepgram** | `aura-asteria-en` | `DEEPGRAM_API_KEY` | $0.0065/1K chars | Low latency |
| **AWS Polly** | `Kajal`, `Aditi` | `AWS_ACCESS_KEY_ID` | $0.004/1K chars | Indian voices |
| **Cartesia** | Various | `CARTESIA_API_KEY` | $0.10/1K chars | Neural |

### Config Example:
```json
"synthesizer": {
  "provider": "edge_tts",
  "voice": "en-IN-NeerjaNeural"
}
```

### Edge TTS Voice Options (FREE):
- **English US**: `en-US-JennyNeural`, `en-US-GuyNeural`
- **English UK**: `en-GB-SoniaNeural`, `en-GB-RyanNeural`
- **English India**: `en-IN-NeerjaNeural`, `en-IN-PrabhatNeural`
- **Hindi**: `hi-IN-SwaraNeural`, `hi-IN-MadhurNeural`

---

## 🎤 STT Providers (The "Ears")

| Provider | Model | Env Key | Cost | Notes |
|----------|-------|---------|------|-------|
| **Deepgram** | `nova-2` | `DEEPGRAM_API_KEY` | $0.0145/min | Best accuracy |
| **Groq** | `whisper-large-v3` | `GROQ_API_KEY` | $0.006/min | Fast & cheap |
| **AssemblyAI** | Default | `ASSEMBLYAI_API_KEY` | $0.015/min | Good accuracy |
| **OpenAI** | `whisper-1` | `OPENAI_API_KEY` | $0.006/min | Reliable |

### Config Example:
```json
"transcriber": {
  "provider": "deepgram",
  "model": "nova-2"
}
```

---

## 📞 Telephony Providers

| Provider | Env Keys | Cost/min | Notes |
|----------|----------|----------|-------|
| **Twilio** | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` | $0.022 | Most popular |
| **Plivo** | `PLIVO_AUTH_ID`, `PLIVO_AUTH_TOKEN` | $0.015 | Budget option |
| **Exotel** | `EXOTEL_SID`, `EXOTEL_TOKEN` | $0.02 | India-focused |

---

## 🚀 Recommended Configurations

### Development (FREE)
```json
{
  "llm": "openrouter/mistralai/mistral-7b-instruct:free",
  "tts": "edge_tts",
  "stt": "groq/whisper-large-v3"
}
```

### Production (Quality)
```json
{
  "llm": "groq/llama-3.1-70b-versatile",
  "tts": "elevenlabs",
  "stt": "deepgram/nova-2"
}
```

### Production (Budget)
```json
{
  "llm": "openrouter/anthropic/claude-3-haiku",
  "tts": "edge_tts",
  "stt": "groq/whisper-large-v3"
}
```

---

## 🔄 Auto-Fallback Logic

Sunona automatically selects providers based on available API keys:

```
1. Check if primary provider's API key exists in .env
2. If yes → Use primary provider
3. If no → Check fallback_1, fallback_2, etc.
4. Use first available provider with valid API key
```

This means you can configure multiple providers, and Sunona will use whichever one has a valid API key!
