# Sunona Voice AI - API Testing Guide

Complete guide to test Sunona's API endpoints for creating agents and making calls.

---

## 🚀 Quick Start

### Step 1: Start the Server

```powershell
# Option A: Main server (agent management)
cd sunona
python -m sunona.server

# Option B: Twilio call server (for phone calls)
python examples/twilio_call_server.py
```

### Step 2: Check Health

```powershell
curl http://localhost:8000/health
```

---

---

## 🛠️ Recommended Workflow (Easiest)

The quickest way to test the API is using the included utility scripts in the `scripts/` folder. They handle authentication and URL encoding automatically.

1. **Verify Connection**: `.\scripts\test_api.bat`
2. **Create Agent**: `.\scripts\create_agent.bat` (Copy the `agent_id`)
3. **Make Call**: `.\scripts\make_call.bat` (Paste the `agent_id`)

---

## 📞 Manual API Workflow (curl)

### 1. Create Agent → Get agent_id

**Using curl.exe (Windows/CMD/PowerShell):**
> [!IMPORTANT]
> Always use `curl.exe` instead of `curl` on Windows to avoid conflict with PowerShell's built-in `curl` alias.

```powershell
curl.exe -X POST http://localhost:8000/agent `
  -H "Content-Type: application/json" `
  -H "X-API-Key: your-api-key" `
  -d "@agent_data/example_recruiter/config.json"
```

**Response:**
```json
{
  "agent_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "state": "created"
}
```

### 2. Make a Call with agent_id

> [!WARNING]
> When calling via URL parameters, the `+` sign in the phone number must be URL-encoded as `%2B`.

```powershell
# Correct (URL encoded +)
curl.exe -X POST "http://localhost:8000/make-call?to=%2B917075xxxxxx&agent_id=f47ac10b-58cc-4372-a567-0e02b2c3d479" -H "X-API-Key: your-api-key"
```

---

## 🔑 API Endpoints Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/agent` | POST | Create new agent |
| `/agent/{id}` | GET | Get agent by ID |
| `/agent/{id}` | PUT | Update agent |
| `/agent/{id}` | DELETE | Delete agent |
| `/agents` | GET | List all agents |
| `/make-call` | POST | Initiate phone call |
| `/chat/{agent_id}` | WS | WebSocket chat |

---

## 📝 Agent Configuration

### Minimal Agent Config

```json
{
  "agent_config": {
    "agent_name": "Sarah",
    "agent_welcome_message": "Hello! How can I help you?",
    "tasks": [{
      "tools_config": {
        "llm_agent": {
          "streaming_model": "gpt-3.5-turbo",
          "agent_flow_type": "streaming"
        },
        "synthesizer": {
          "provider": "elevenlabs",
          "voice": "Rachel"
        },
        "transcriber": {
          "provider": "deepgram"
        }
      }
    }]
  },
  "agent_prompts": {
    "task_1": {
      "system_prompt": "You are a helpful AI assistant."
    }
  }
}
```

---

## 🧪 Testing with Insomnia/Postman

### Import Collection
1. Open Insomnia or Postman
2. Import `docs/sunona-api-collection.json`
3. Set environment variables:
   - `BASE_URL`: `http://localhost:8000`
   - `API_KEY`: Your API key

### Test Sequence
1. **Health Check** → Verify server is running
2. **Create Agent** → Copy `agent_id` from response
3. **Get Agent** → Verify agent was created
4. **Make Call** → Use `agent_id` to make call

---

## 🐳 Docker Setup

```powershell
cd local_setup
docker-compose up --build
```

This starts:
- Redis (port 6379)
- Sunona API (port 8000)
- Twilio Server (port 8001)
- Ngrok tunnel

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Add `X-API-Key` header |
| 404 Agent not found | Check agent_id is correct |
| 500 Twilio error | Verify TWILIO_* env vars |
| Connection refused | Start the server first |

---

## 📚 More Resources

- [README.md](../README.md) - Project overview
- [.env.example](../.env.example) - Environment variables
- [examples/](../examples/) - More examples
