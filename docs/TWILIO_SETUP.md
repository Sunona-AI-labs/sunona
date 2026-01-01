# Twilio Setup Guide for Sunona Voice AI

Quick guide to configure Twilio for making phone calls with Sunona.

---

## 🚀 Quick Setup

### 1. Create Twilio Account
Go to https://www.twilio.com/console and sign up (free trial available).

### 2. Get Your Credentials
From the Twilio Console dashboard, copy:
- **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Auth Token**: Click "Show" to reveal

### 3. Get a Phone Number
Go to **Phone Numbers** → **Buy a Number** (or use trial number).

### 4. Update Your .env File
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WEBHOOK_URL=https://your-ngrok-url.ngrok-free.dev
```

### 5. Start ngrok (for webhooks)
Twilio needs to reach your local server:
```powershell
ngrok http 8000
```
Copy the HTTPS URL (e.g., `https://abc123.ngrok-free.dev`) to `TWILIO_WEBHOOK_URL`.

---

## 📞 Making a Call

### Using the Script
```powershell
.\scripts\make_call.bat
```

### Using curl
```powershell
curl -X POST "http://localhost:8000/make-call?to=+1234567890&agent_id=your-agent-id" `
  -H "X-API-Key: YOUR_MASTER_KEY"
```

---

## 🔧 If Twilio Not Configured

The API will return:
```json
{
  "error": "twilio_not_configured",
  "message": "Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN...",
  "docs": "https://www.twilio.com/console"
}
```

---

## 💰 Twilio Pricing
- **Trial Account**: Free calls to verified numbers only
- **Paid Account**: ~$0.022/min for outbound calls (US)

---

## 📚 More Info
- [Twilio Console](https://www.twilio.com/console)
- [Twilio Pricing](https://www.twilio.com/voice/pricing)
- [ngrok](https://ngrok.com/)
