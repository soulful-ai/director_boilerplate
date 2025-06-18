#!/bin/bash

# Director MCP Configuration Generator
# Generates .mcp.json at workspace root for Claude access

# Source Director's .env file
if [[ -f ".env" ]]; then
    source .env
else
    echo "Error: Director .env file not found. Run setup-environment.sh first."
    exit 1
fi

# Check required variables
if [[ -z "$MCP_CLI_DIR" || -z "$ALLOWED_DIR" ]]; then
    echo "Error: MCP_CLI_DIR and ALLOWED_DIR must be set in .env"
    exit 1
fi

# Director outputs to workspace root for Claude access
if [[ -f ".mcp.json.template" ]]; then
    envsubst < .mcp.json.template > ../.mcp.json
    echo "Generated ../.mcp.json (at workspace root) with paths:"
else
    echo "Error: .mcp.json.template not found"
    exit 1
fi

echo "  MCP_CLI_DIR: $MCP_CLI_DIR"
echo "  ALLOWED_DIR: $ALLOWED_DIR"