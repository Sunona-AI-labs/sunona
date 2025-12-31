#!/bin/bash
# Sunona Voice AI - Quick Build Script (Linux/Mac)
# Uses BuildKit for faster Docker builds

echo "========================================"
echo "   SUNONA VOICE AI - QUICK BUILD"
echo "========================================"
echo ""

# Enable BuildKit
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed!"
    exit 1
fi

echo "BuildKit enabled for faster builds!"
echo ""

echo "Select build option:"
echo "  1. Build main app only"
echo "  2. Build all services"
echo "  3. Build with no cache (fresh)"
echo "  4. Build and start"
echo ""
read -p "Enter choice (1-4): " OPTION

cd ..

case $OPTION in
    1)
        echo ""
        echo "Building sunona-app..."
        docker build -f local_setup/Dockerfile -t sunona-app:latest .
        ;;
    2)
        echo ""
        echo "Building all services..."
        docker compose -f local_setup/docker-compose.yml build
        ;;
    3)
        echo ""
        echo "Building fresh (no cache)..."
        docker compose -f local_setup/docker-compose.yml build --no-cache
        ;;
    4)
        echo ""
        echo "Building and starting..."
        docker compose -f local_setup/docker-compose.yml up -d --build
        ;;
    *)
        echo "Invalid choice. Building main app..."
        docker build -f local_setup/Dockerfile -t sunona-app:latest .
        ;;
esac

echo ""
echo "========================================"
echo "   BUILD COMPLETE"
echo "========================================"
echo ""
echo "To verify: docker images | grep sunona"
echo ""
