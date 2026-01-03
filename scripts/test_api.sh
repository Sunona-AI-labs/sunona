#!/bin/bash

# ============================================================
# Sunona AI - Test API Health (Linux/macOS)
# Quick health check for all endpoints
# ============================================================

echo ""
echo "========================================"
echo "  SUNONA AI - API HEALTH CHECK (BASH)"
echo "========================================"
echo ""

SERVER_URL="http://localhost:8000"
API_KEY="49149399e6b7addee08fc659c9b35944191521b2124b82c7d059beec66690f5e"

echo "Testing: $SERVER_URL"
echo ""

echo "[1/4] Root endpoint..."
curl -s "$SERVER_URL/"
echo ""
echo ""

echo "[2/4] Health check..."
curl -s "$SERVER_URL/health"
echo ""
echo ""

echo "[3/4] Liveness probe..."
curl -s "$SERVER_URL/health/liveness"
echo ""
echo ""

echo "[4/4] List agents..."
curl -s -H "X-API-Key: $API_KEY" "$SERVER_URL/agents"
echo ""
echo ""

echo "========================================"
echo "Health check complete!"
echo "========================================"
echo ""
