#!/bin/bash
# Sunona Voice AI - Linux/Mac Start Script
# Production-ready local setup

echo "========================================"
echo "   SUNONA VOICE AI - LOCAL SETUP"
echo "========================================"
echo ""

# Check if .env exists
if [ ! -f "../.env" ]; then
    echo "[WARNING] .env file not found!"
    echo "Creating from .env.example..."
    cp "../.env.example" "../.env"
    echo ""
    echo "[ACTION REQUIRED] Edit .env with your API keys!"
    echo "Run: nano ../.env"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed!"
    echo "Please install Docker from https://docker.com"
    exit 1
fi

echo ""
echo "Select deployment mode:"
echo "  1. Basic (App + Redis only)"
echo "  2. Full (App + Redis + PostgreSQL)"
echo "  3. Development (All + Ngrok)"
echo "  4. Production (All + Monitoring)"
echo ""
read -p "Enter choice (1-4): " MODE

case $MODE in
    1)
        echo ""
        echo "Starting Basic Setup..."
        docker compose up -d sunona-app redis
        ;;
    2)
        echo ""
        echo "Starting Full Setup..."
        docker compose up -d sunona-app redis postgres
        ;;
    3)
        echo ""
        echo "Starting Development Setup..."
        docker compose --profile dev up -d
        ;;
    4)
        echo ""
        echo "Starting Production Setup..."
        docker compose --profile monitoring up -d
        ;;
    *)
        echo "Invalid choice. Starting Basic Setup..."
        docker compose up -d sunona-app redis
        ;;
esac

echo ""
echo "========================================"
echo "   SERVICES STARTED"
echo "========================================"
echo ""
echo "Sunona API:    http://localhost:8000"
echo "Health Check:  http://localhost:8000/health"
echo ""

if [ "$MODE" == "3" ]; then
    echo "Ngrok Console: http://localhost:4040"
fi

if [ "$MODE" == "4" ]; then
    echo "Prometheus:    http://localhost:9090"
    echo "Grafana:       http://localhost:3000"
fi

echo ""
echo "To view logs:  docker compose logs -f"
echo "To stop:       docker compose down"
echo ""
