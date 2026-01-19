# 🎙️ Sunona Voice AI - Interactive Demos

Professional, high-performance interfaces to experience Sunona's voice AI capabilities.

## 🎨 Professional Gradio Interface
The primary web demo provides a unified experience for all Sunona modules.
- **Run**: `python gradio_app.py`
- **Features**: Professional SVG icons, modern gradient UI, and real-time conversation history.
- **Robustness**: Integrated 5-tier TTS fallback system for enterprise-grade reliability.

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
   ```

2. **Setup Credentials**:
   ```bash
   cp .env.example .env
   # Add your GOOGLE_API_KEY, DEEPGRAM_API_KEY, etc.
   ```

3. **Launch**:
   ```bash
   python gradio_app.py
   ```

---

## 🏗️ Demo Capabilities

| Demo | Description | Pipeline |
|------|-------------|----------|
| **Text-to-Text** | Modern chat interface | Text → LLM → Text |
| **Text-to-Speech** | Voice response with autoplay | Text → LLM → TTS → Audio |
| **Speech-to-Speech** | Fully hands-free voice AI | Audio → STT → LLM → TTS → Audio |
| **Phone Call** | Real Twilio telephony testing | Twilio → Sunona API → Voice |

## 🛡️ Tiered TTS Fallback
The demos are engineered to never lose their voice:
1. **User Selected** (e.g., ElevenLabs)
2. **ElevenLabs** (Premium fallback)
3. **OpenAI TTS** (Reliable fallback)
4. **Play.ht** (Secondary fallback)
5. **Edge TTS (Free)** (Final fail-safe - always works)

---

## 🐳 Deployment (Cloud Ready)

These demos are optimized for cloud platforms like **Render**, **Railway**, and **AWS**:
- **Render**: Uses `render.yaml` and handles Gradio dependencies automatically.
- **Docker**: `docker build -t sunona-demo .`
- **Static Assets**: Unique audio file naming prevents collision in multi-user environments.
