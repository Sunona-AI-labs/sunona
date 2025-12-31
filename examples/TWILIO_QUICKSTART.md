# Twilio Call Server - Complete Step-by-Step Guide

## Prerequisites

| Requirement | How to Get |
|-------------|------------|
| Python 3.9+ | [python.org](https://www.python.org/downloads/) |
| Twilio Account | [twilio.com/try-twilio](https://www.twilio.com/try-twilio) |
| ngrok | [ngrok.com/download](https://ngrok.com/download) |

---

## Step 1: Get Your Credentials

### 1.1 Twilio Credentials
1. Go to [Twilio Console](https://console.twilio.com)
2. Copy your **Account SID** (starts with `AC`)
3. Copy your **Auth Token**
4. Buy a phone number with **Voice** capability

### 1.2 AI Provider Keys

| Provider | Purpose | Get Key From |
|----------|---------|--------------|
| **OpenRouter** (FREE!) | LLM | [openrouter.ai/keys](https://openrouter.ai/keys) |
| Deepgram | Speech-to-Text | [console.deepgram.com](https://console.deepgram.com) |
| ElevenLabs | Text-to-Speech | [elevenlabs.io](https://elevenlabs.io) |

> **Note**: We're using **OpenRouter** for LLM because it provides free models like Mistral 7B!

---

## Step 2: Configure Your .env File

Edit your `.env` file with your credentials:

```bash
# =============================================================================
# Twilio
# =============================================================================
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

# =============================================================================
# LLM Provider - OpenRouter (FREE models available!)
# =============================================================================
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free

# Alternative: OpenAI (if you prefer)
# OPENAI_API_KEY=sk-xxxxxxxx

# =============================================================================
# Speech-to-Text - Deepgram
# =============================================================================
DEEPGRAM_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# =============================================================================
# Text-to-Speech - ElevenLabs
# =============================================================================
ELEVENLABS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL  
#(choose own voice id from elevenlabs)

# =============================================================================
# Webhook URL (will be updated in Step 4)
# =============================================================================
TWILIO_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.dev
```

---

## Step 3: Install Dependencies

Open **PowerShell** as Administrator:

```powershell
cd "d:\one cloud\OneDrive\Desktop\sunona"

# Activate virtual environment (if you have one)
.\venv\Scripts\Activate

# Install required packages
pip install twilio python-dotenv uvicorn fastapi litellm
```

---

## Step 4: Start ngrok (Terminal 1)

**IMPORTANT**: Keep this terminal open!

```powershell
# In Terminal 1
ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.dev -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.dev`)

### Update .env with ngrok URL:
Edit your `.env` file and set:
```
TWILIO_WEBHOOK_URL=https://abc123.ngrok-free.dev
```

---

## Step 5: Start the Call Server (Terminal 2)

Open a **NEW PowerShell terminal**:

```powershell
# In Terminal 2
cd "d:\one cloud\OneDrive\Desktop\sunona"
.\venv\Scripts\Activate

# Start the server
python examples/twilio_call_server.py
```

You should see:
```
🎙️  SUNONA VOICE AI - TWILIO CALL SERVER
✅ Twilio handler initialized
✅ LLM initialized (OpenRouter: mistralai/mistral-7b-instruct:free)
✅ Transcriber initialized (Deepgram)
✅ Synthesizer initialized (ElevenLabs)
🚀 Server ready at https://abc123.ngrok-free.dev
📞 Twilio phone: +1234567890
```

> **Note**: The server will use **OpenRouter** if configured, otherwise falls back to OpenAI.

---

## Step 6: Make a Call (Terminal 3)

Open a **THIRD PowerShell terminal**:

### For Indian Numbers (+91)

```powershell
# Format: +91 followed by 10 digits (no spaces!)
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/make-call?to=%2B917075488xxx"
```

### For US Numbers (+1)

```powershell
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/make-call?to=%2B11234567890"
```

### Using curl.exe (alternative)

```powershell
curl.exe -X POST "http://localhost:8000/make-call?to=+917075488xxx"
```

### Expected Response:
```json
{
  "success": true,
  "call_sid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "to": "+917075488xxx",
  "from": "+1234567890",
  "status": "initiated"
}
```

---

## Quick Reference: Phone Number Formats

| Country | Format | Example |
|---------|--------|---------|
| India | +91 + 10 digits | `+917075488xxx` |
| USA | +1 + 10 digits | `+11234567890` |
| UK | +44 + 10 digits | `+441234567890` |

**Note**: In PowerShell, `+` must be URL encoded as `%2B`

---

## Step 7: Verify the Call

1. Your phone should ring
2. When you answer, the AI assistant will greet you
3. Speak naturally - the AI will respond!

---

## LLM Provider Options

The server supports multiple LLM providers:

| Provider | Model | Cost | How to Enable |
|----------|-------|------|---------------|
| **OpenRouter** (default) | mistralai/mistral-7b-instruct:free | **FREE** | Set `OPENROUTER_API_KEY` |
| OpenRouter | gpt-4o-mini | ~$0.15/1M tokens | Set `OPENROUTER_MODEL=openai/gpt-4o-mini` |
| OpenAI | gpt-4o-mini | ~$0.15/1M tokens | Set `OPENAI_API_KEY` |

> **Tip**: OpenRouter's free Mistral model works great for basic voice AI!

---

## Troubleshooting

### "Twilio not configured"
```powershell
# Check your .env file has correct Twilio credentials
Get-Content .env | Select-String "TWILIO"
```

### "No LLM configured"
- Check that `OPENROUTER_API_KEY` is set in your `.env`
- Or set `OPENAI_API_KEY` as a fallback

### "Connection refused" on make-call
- Make sure the server is running (Step 5)
- Check Terminal 2 for errors

### Call connects but no audio
- Verify ngrok is still running (Terminal 1)
- Check that `TWILIO_WEBHOOK_URL` in `.env` matches your ngrok URL
- Restart the server after updating `.env`

### "Unable to call this number"
- Make sure your Twilio account has international calling enabled
- Check your Twilio balance
- For trial accounts, the recipient must be verified

---

## Terminal Layout Summary

```
┌─────────────────────────────────────────────────────────┐
│ Terminal 1: ngrok http 8000                             │
│ Status: Keep running, shows connection logs             │
├─────────────────────────────────────────────────────────┤
│ Terminal 2: python examples/twilio_call_server.py       │
│ Status: Keep running, shows call processing logs        │
├─────────────────────────────────────────────────────────┤
│ Terminal 3: Make API calls                              │
│ Command: Invoke-RestMethod -Method POST -Uri "..."      │
└─────────────────────────────────────────────────────────┘
```

---

## Cost Estimate (with OpenRouter Free Model)

| Service | Cost per Minute |
|---------|----------------|
| Twilio (India calls) | ~$0.05/min |
| Deepgram STT | ~$0.015/min |
| **OpenRouter (Mistral Free)** | **FREE** |
| ElevenLabs TTS | ~$0.02/min |
| **Total** | **~$0.085/min** |

> Using OpenRouter's free model saves you ~$0.01/min on LLM costs!

---

## API Endpoints

| Method | Endpoint | Description | Example |
|--------|----------|-------------|---------|
| GET | `/` | Health check | `http://localhost:8000` |
| POST | `/make-call?to=+{number}` | Make call | See Step 6 |
| GET | `/calls` | List active calls | `Invoke-RestMethod http://localhost:8000/calls` |
| POST | `/hangup/{call_sid}` | End a call | `Invoke-RestMethod -Method POST "http://localhost:8000/hangup/CA123"` |

---

## Ready to Call!

```powershell
# Make a call to Indian number
Invoke-RestMethod -Method POST -Uri "http://localhost:8000/make-call?to=%2B917075488xxx"
```
