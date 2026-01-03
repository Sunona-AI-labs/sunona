#!/bin/bash

# ============================================================
# Sunona AI - Create Agent Script (Linux/macOS)
# Creates an agent and displays the agent_id
# ============================================================

echo ""
echo "========================================"
echo "  SUNONA AI - CREATE AGENT (BASH)"
echo "========================================"
echo ""

SERVER_URL="http://localhost:8000"
CONFIG_FILE="agent_data/example_recruiter/config.json"
API_KEY="49149399e6b7addee08fc659c9b35944191521b2124b82c7d059beec66690f5e"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: Config file not found: $CONFIG_FILE"
    echo "Please run this from the sunona project root directory."
    exit 1
fi

echo "Creating agent from: $CONFIG_FILE"
echo "Server: $SERVER_URL"
echo ""

# Create agent using curl
echo "Sending request..."
echo ""

curl -X POST "$SERVER_URL/agent" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d @"$CONFIG_FILE"

echo ""
echo ""
echo "========================================"
echo "Copy the agent_id from above to use in make_call.sh"
echo "========================================"
echo ""
