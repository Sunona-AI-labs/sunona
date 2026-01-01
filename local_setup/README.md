# Sunona Voice AI - Local Setup

Production-ready Docker deployment for Sunona Voice AI.

## Quick Start

### Windows
```powershell
cd local_setup
.\start.bat
```

### Linux/Mac
```bash
cd local_setup
chmod +x start.sh
./start.sh
```

## 🚀 Quick Build with BuildKit

BuildKit provides **10x faster rebuilds** with intelligent caching.

### Windows
```powershell
cd local_setup
.\build.bat
```

### Linux/Mac
```bash
cd local_setup
chmod +x build.sh
./build.sh
```

### Manual Build (with BuildKit)
```bash
# Enable BuildKit
set DOCKER_BUILDKIT=1          # Windows (cmd)
$env:DOCKER_BUILDKIT=1         # Windows (PowerShell)
export DOCKER_BUILDKIT=1       # Linux/Mac

# Build all services
docker compose build

# Build with no cache (fresh)
docker compose build --no-cache

# Build and start
docker compose up -d --build
```

### BuildKit Cache Mounts

Our Dockerfiles use cache mounts for faster builds:

```dockerfile
# Pip cache - reuses downloaded packages
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Apt cache - reuses downloaded packages  
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get install -y ffmpeg curl
```

### BuildKit Benefits
- 🚀 **10x faster rebuilds** - Caches pip and apt packages
- 📦 **Smaller context** - .dockerignore excludes unnecessary files
- ⚡ **Parallel builds** - Multiple stages build simultaneously
- 💾 **Smart caching** - Only rebuilds changed layers

---

## Deployment Modes

| Mode | Services | Use Case |
|------|----------|----------|
| **Basic** | App + Redis | Development, testing |
| **Full** | App + Redis + PostgreSQL | Production without monitoring |
| **Development** | All + Ngrok | Local dev with Twilio webhooks |
| **Production** | All + Monitoring | Full production with Prometheus/Grafana |

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| `sunona-app` | 8000 | Main API server |
| `twilio-server` | 8001 | Twilio call handler |
| `redis` | 6379 | Session storage |
| `postgres` | 5432 | Database |
| `chromadb` | 8001 | Vector store (RAG profile) |
| `ngrok` | 4040 | Tunnel console (dev profile) |
| `prometheus` | 9090 | Metrics (monitoring profile) |
| `grafana` | 3000 | Dashboard (monitoring profile) |

---

## Configuration

### Required Environment Variables

```bash
# Copy example to .env in project root
cp ../.env.example ../.env
```

**Minimum required:**
```bash
OPENROUTER_API_KEY=sk-or-v1-xxx    # LLM (FREE)
DEEPGRAM_API_KEY=xxx               # STT
ELEVENLABS_API_KEY=xxx             # TTS
DEFAULT_ORGANIZATION_ID=org_default # Multi-tenancy
SUNONA_MASTER_KEY=xxx              # API Security
```

**For Twilio calls:**
```bash
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+1xxx
NGROK_AUTH_TOKEN=xxx
```

---

## Commands

### Start Services
```bash
# Basic
docker compose up -d sunona-app redis

# With database
docker compose up -d sunona-app redis postgres

# With ngrok (for Twilio)
docker compose --profile dev up -d

# With monitoring
docker compose --profile monitoring up -d

# Everything
docker compose --profile dev --profile monitoring --profile rag up -d
```

### View Logs
```bash
docker compose logs -f sunona-app
docker compose logs -f twilio-server
```

### Stop Services
```bash
docker compose down

# Remove volumes too
docker compose down -v
```

### Rebuild
```bash
# With BuildKit (faster)
DOCKER_BUILDKIT=1 docker compose build sunona-app

# Without cache
docker compose build --no-cache sunona-app

# Build and start
docker compose up -d --build
```

---

## Database

PostgreSQL is initialized with:
- Users & API keys tables
- Billing accounts & transactions
- Knowledge bases & chunks (with vector support)
- Agents configuration
- Call logs

**Default admin:** `admin@sunona.ai` / `admin123`

---

## Health Checks

All services have health checks:
```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

---

## Profiles

Use profiles to enable optional services:

```bash
# Enable RAG (ChromaDB)
docker compose --profile rag up -d

# Enable development tools (Ngrok)
docker compose --profile dev up -d

# Enable monitoring (Prometheus + Grafana)
docker compose --profile monitoring up -d
```

---

## Production Checklist

- [x] Set strong `JWT_SECRET` and `SUNONA_MASTER_KEY`
- [x] Review Production Hardening Audit report
- [ ] Change default PostgreSQL password
- [ ] Configure Stripe for billing
- [ ] Set up SMTP for email notifications
- [ ] Configure SSL/TLS (use reverse proxy)
- [ ] Set `SUNONA_DEBUG=false`
- [ ] Set proper resource limits
- [ ] Configure backups for postgres-data volume

---

## Troubleshooting

### Container won't start
```bash
docker compose logs sunona-app
```

### Database connection issues
```bash
docker compose exec postgres psql -U sunona -c "SELECT 1"
```

### Redis connection issues
```bash
docker compose exec redis redis-cli ping
```

### Reset everything
```bash
docker compose down -v
docker compose up -d
```

### Build issues
```bash
# Enable BuildKit and rebuild
DOCKER_BUILDKIT=1 docker compose build --no-cache
```
