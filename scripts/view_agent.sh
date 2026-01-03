#!/bin/bash

# ============================================================
# Sunona AI - View Agent Details Script (Linux/macOS)
# Displays agent name, prompt, and user profiles
# ============================================================

# Project paths
CONFIG_FILE="agent_data/example_recruiter/config.json"
USERS_FILE="agent_data/example_recruiter/users.json"

echo ""
echo "========================================"
echo "  SUNONA AI - AGENT VIEWER (LOCAL)"
echo "========================================"

# Check if required tools are installed (jq is highly recommended for JSON)
if ! command -v jq &> /dev/null; then
    echo "TIP: Install 'jq' for better formatted output (e.g., sudo apt install jq)"
    HAS_JQ=false
else
    HAS_JQ=true
fi

# 1. Display Agent Name
echo ""
echo "--- [ AGENT NAME ] ---"
if [ "$HAS_JQ" = true ]; then
    cat "$CONFIG_FILE" | jq -r '.agent_config.agent_name'
else
    grep -oP '"agent_name":\s*"\K[^"]+' "$CONFIG_FILE"
fi

# 2. Display System Prompt
echo ""
echo "--- [ SYSTEM PROMPT ] ---"
if [ "$HAS_JQ" = true ]; then
    cat "$CONFIG_FILE" | jq -r '.agent_prompts.task_1.system_prompt'
else
    # Simple extraction for non-jq users (might not be pretty)
    sed -n '/"system_prompt":/,/"/p' "$CONFIG_FILE" | sed 's/.*"system_prompt": "//;s/".*//'
fi

# 3. Display Recognized Users
echo ""
echo "--- [ RECOGNIZED USERS ] ---"
if [ "$HAS_JQ" = true ]; then
    cat "$USERS_FILE" | jq '.'
else
    cat "$USERS_FILE"
fi

echo ""
echo "========================================"
echo "View complete!"
echo "========================================"
echo ""
