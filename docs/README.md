# Sunona Voice AI - Documentation Index

Welcome to the Sunona documentation! This folder contains all technical docs, guides, and references.

---

## 📚 Documentation

### Getting Started
| Document | Description |
|----------|-------------|
| [API Testing Guide](API_TESTING_GUIDE.md) | How to test Sunona APIs with curl and Insomnia |
| [Provider Reference](PROVIDER_REFERENCE.md) | All LLM, TTS, STT providers with costs |

---

## 🧪 API Testing

### Insomnia/Postman Collection
Import `sunona-api-collection.json` into Insomnia or Postman for pre-configured API requests.

### Quick Test (Windows)
```powershell
cd sunona
.\scripts\test_api.bat     # Health check
.\scripts\create_agent.bat # Create agent
.\scripts\make_call.bat    # Make call
```

---

## 📁 Related Folders

| Folder | Purpose |
|--------|---------|
| `../examples/` | Example scripts and demos |
| `../agent_data/` | Agent configurations |
| `../local_setup/` | Docker deployment files |
| `../scripts/` | Helper scripts |
