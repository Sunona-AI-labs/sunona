#!/bin/bash

# ============================================================
# Sunona AI - Make Call Script (Linux/macOS)
# Makes a phone call using an agent
# ============================================================

echo ""
echo "========================================"
echo "  SUNONA AI - MAKE CALL (BASH)"
echo "========================================"
echo ""

SERVER_URL="http://localhost:8000"
API_KEY="49149399e6b7addee08fc659c9b35944191521b2124b82c7d059beec66690f5e"

# Get parameters
if [ -z "$1" ]; then
    read -p "Enter phone number with country code (e.g., +917075xxxxxx): " PHONE_NUMBER
else
    PHONE_NUMBER=$1
fi

if [ -z "$2" ]; then
    read -p "Enter agent_id (from create_agent): " AGENT_ID
else
    AGENT_ID=$2
fi

echo ""
echo "Making call to: $PHONE_NUMBER"
echo "Using agent: $AGENT_ID"
echo ""

# Encode phone number for URL (handles + sign) using Python
ENCODED_PHONE=$(python3 -c "import urllib.parse; print(urllib.parse.quote('''$PHONE_NUMBER'''))")

# Make the call
curl -X POST "$SERVER_URL/make-call?to=$ENCODED_PHONE&agent_id=$AGENT_ID" \
  -H "X-API-Key: $API_KEY"

echo ""
echo ""
echo "========================================"
echo "Call initiated! Check the server logs."
echo "========================================"
echo ""
