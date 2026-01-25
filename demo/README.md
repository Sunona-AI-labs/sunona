# 🎙️ Sunona Voice AI - Interactive Demos

Professional, high-performance interfaces to experience Sunona's voice AI capabilities.

## 🎨 Unified Gradio Interface (`gradio_app.py`)
The primary web demo provides a unified experience for all Sunona modules, now with integrated **Real-time Telephony**.
- **Run**: `python gradio_app.py`
- **New Feature**: **Real-time Twilio Streaming** - When you initiate a call, the app now uses WebSockets to stream audio directly between Twilio and the Sunona backend.
- **Robustness**: Integrated 5-tier TTS fallback system for enterprise-grade reliability.
- **UI**: Professional SVG icons, modern gradient UI, and real-time conversation history.

## 📞 Twilio Trial Tester (`twilio_trial_test.py`)
A dedicated script for testing Twilio Trial accounts with real-time streaming.
- **Run**: `python twilio_trial_test.py`
- **Usage**: Use this to verify your Twilio credentials and voice settings independently of the main UI.

## 🎤 Hands-Free VAD Assistant
A standalone console experience for true natural voice interaction.
- **Run**: `python hands_free_assistant.py`
- **Speech Detection**: Uses advanced VAD to automatically detect when you start and stop talking.
- **Barge-In**: Interrupt the AI mid-sentence for a more human-like conversation.

---

## 🚀 Quick Start (Local)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Setup Credentials**:
   ```bash
   # Add your TWILIO_ACCOUNT_SID, DEEPGRAM_API_KEY, etc. to your .env
   ```

3. **Expose with ngrok**:
   ```bash
   ngrok http 7860
   ```

4. **Update Twilio Webhook**:
   - URL: `https://your-ngrok.dev/voice`
   - Method: `POST`

---

## 🏗️ Demo Capabilities

| Demo | Description | Status |
|------|-------------|--------|
| **Text-to-Text** | Modern chat interface | ✅ Live |
| **Text-to-Speech** | Voice response with autoplay | ✅ Live |
| **Speech-to-Speech** | Fully hands-free voice AI | ✅ Live |
| **Phone Call** | **Real-time AI Telephony** | 🚀 Integrated (WebSocket) |

---

## 🏗️ Deployment (Render)

This branch (`render-demo`) is optimized for **Render Blueprint** deployments.

1. **Branch**: Ensure you are on the `render-demo` branch.
2. **Blueprint**: Connect your repository to Render via the "Blueprint" feature.
3. **Environment**: Fill in the `sunona-secrets` group with your API keys.
4. **URL**: Point your Twilio number to `https://your-app.onrender.com/voice`.

---

## 🛡️ Tiered TTS Fallback
The demos are engineered to never lose their voice:
1. **User Selected** (e.g., ElevenLabs)
2. **ElevenLabs** (Premium fallback)
3. **OpenAI TTS** (Reliable fallback)
4. **Edge TTS (Free)** (Always works)
