# 🎙️ Sunona Voice AI - Demo

Interactive demos showcasing Sunona's voice AI capabilities.

## Quick Start

```bash
cd demo
cp .env.example .env
# Edit .env with your API keys
pip install -r requirements.txt
python gradio_app.py
# Open http://localhost:7860
```

## Demos

| Demo | Description | Requirements |
|------|-------------|--------------|
| 💬 Text-to-Text | Chat with AI | GOOGLE_API_KEY |
| 🔊 Text-to-Speech | Ask in text, hear answer | GOOGLE_API_KEY |
| 🎙️ Speech-to-Speech | Hands-free voice conversation | GOOGLE_API_KEY + DEEPGRAM_API_KEY |
| 📞 Twilio Call | Real phone call with AI | All + TWILIO credentials |

## API Keys

| API | Get Key | Free Tier |
|-----|---------|-----------|
| Gemini | [AI Studio](https://aistudio.google.com/app/apikey) | 15 RPM |
| Deepgram | [Console](https://console.deepgram.com/) | $200 credit |
| ElevenLabs | [Settings](https://elevenlabs.io/app/settings/api-keys) | 10K chars/mo |
| Twilio | [Console](https://twilio.com/console) | $15.50 credit |

## Deployment

```bash
# Docker
docker build -t sunona-demo .
docker run -p 7860:7860 --env-file .env sunona-demo

# Render
# Use render.yaml

# Railway
# Use railway.json
```
