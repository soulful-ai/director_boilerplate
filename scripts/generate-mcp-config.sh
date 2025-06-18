#!/bin/bash

# PM Director MCP Configuration Generator
# Always generates .mcp.json at workspace root for Claude access

# Source PM's .env file
if [[ -f ".env" ]]; then
    source .env
elif [[ -f "../pm/.env" ]]; then
    source ../pm/.env
else
    echo "Error: PM .env file not found. Run setup-environment.sh first."
    exit 1
fi

# Check required variables
if [[ -z "$MCP_CLI_DIR" || -z "$ALLOWED_DIR" ]]; then
    echo "Error: MCP_CLI_DIR and ALLOWED_DIR must be set in PM's .env"
    exit 1
fi

# PM Director always outputs to workspace root
# This is a special behavior for PM Director only
if [[ -f ".mcp.json.template" ]]; then
    envsubst < .mcp.json.template > ../.mcp.json
    echo "Generated ../.mcp.json (at workspace root) with paths:"
else
    echo "Error: .mcp.json.template not found"
    exit 1
fi

echo "  MCP_CLI_DIR: $MCP_CLI_DIR"
echo "  ALLOWED_DIR: $ALLOWED_DIR"