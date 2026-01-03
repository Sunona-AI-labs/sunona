# Sunona AI - Quick Start Scripts 🚀

This folder contains helper scripts to quickly interact with the Sunona Voice AI API. These scripts simplify agent creation, health monitoring, and initiating phone calls.

---

## 📋 Prerequisites

1. **Start the Server**: The Sunona API server must be running.
   ```powershell
   python -m sunona.server
   ```
   *Note: If you get a "socket access forbidden" error, it usually means the server is already running in another window or port 8000 is occupied.*

2. **API Key**: These scripts are pre-configured with your `SUNONA_MASTER_KEY` for authentication.

---

## 🛠️ Script Overview

### 1. `test_api.bat` (Health Check)
**Purpose:** Verifies that the server is up and responsive.
- **Run this first** to ensure connection.
- **Endpoints tested**: Root, `/health`, `/health/liveness`, and `/agents`.
- **Command (Windows):** `.\scripts\test_api.bat`
- **Command (Linux/macOS):** `bash ./scripts/test_api.sh`

### 2. `create_agent.bat` (Create AI Agent)
**Purpose:** Registers a new AI voice agent in the system.
- **Config used**: `agent_data/example_recruiter/config_minimal.json` (currently configured as "Priya", the Campus Recruiter).
- **Output**: Returns a JSON object with a unique `agent_id`.
- **Action**: **Copy the `agent_id`** from the output; you will need it to make calls.
- **Command (Windows):** `.\scripts\create_agent.bat`
- **Command (Linux/macOS):** `bash ./scripts/create_agent.sh`

### 3. `make_call.bat` (Initiate Phone Call)
**Purpose:** Triggers an outbound phone call using a specific agent.
- **Requirements**: Requires a valid `agent_id` and a phone number in E.164 format (e.g., `+917075xxxxxx`).
- **Interactive**: The script will prompt you for the phone number and agent ID if not provided as arguments.
- **Command (Windows):** `.\scripts\make_call.bat`
- **Command (Linux/macOS):** `bash ./scripts/make_call.sh`

### 4. `view_agent.bat` (View Agent Details)
**Purpose:** Displays the local configuration including agent name, system prompt, and user profiles.
- **Command (Windows):** `.\scripts\view_agent.bat`
- **Command (Linux/macOS):** `bash ./scripts/view_agent.sh`

---

## 🧪 Recommended Workflow

1. **Verify Connection**:
   ```powershell
   .\scripts\test_api.bat
   ```
2. **Create your Recruiter Agent**:
   ```powershell
   .\scripts\create_agent.bat
   ```
   *(Copy the generated `agent_id`)*

3. **Call yourself**:
   ```powershell
   .\scripts\make_call.bat
   ```
   *(Paste the `agent_id` when prompted)*

---

## 🔧 Troubleshooting

- **"Invalid API Key"**: Ensure the `API_KEY` in the `.bat` files matches the `SUNONA_MASTER_KEY` in your `.env` file.
- **"Connection Refused"**: The server is likely not running. Start it with `python -m sunona.server`.
- **"TTS Provider Not Supported"**: Ensure your `config.json` uses supported providers like `elevenlabs` or `deepgram`.
- **PowerShell Issues**: These scripts use `curl.exe` explicitly to avoid conflicts with PowerShell's `curl` alias. They are fully compatible with both CMD and PowerShell.
- **Phone Number Encoding**: `make_call.bat` automatically handles URL encoding for the `+` prefix in E.164 phone numbers.

---

## 📚 Related Documentation
- [API Testing Guide](../docs/API_TESTING_GUIDE.md)
- [Twilio Setup Guide](../docs/TWILIO_SETUP.md)
- [Provider Reference](../docs/PROVIDER_REFERENCE.md)
