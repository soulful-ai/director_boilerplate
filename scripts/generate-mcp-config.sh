#!/bin/bash

# Generate MCP configuration from template

echo "🔧 Generating MCP configuration..."

# Load environment variables
if [ -f .env.detected ]; then
    export $(cat .env.detected | grep -v '^#' | xargs)
fi

if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if template exists
if [ ! -f .mcp.json.template ]; then
    echo "❌ Error: .mcp.json.template not found!"
    exit 1
fi

# Generate .mcp.json from template
envsubst < .mcp.json.template > .mcp.json

echo "✅ Generated .mcp.json with environment-specific values"
echo ""
echo "MCP servers configured:"
echo "- nx-mcp: Nx workspace tools"
echo "- cli_use: Director CLI on port ${DIRECTOR_PORT:-9000}"

# Add actor MCP servers if they exist
if [ -d "packages" ]; then
    for actor_dir in packages/*/; do
        if [ -d "$actor_dir" ] && [ -f "$actor_dir/.mcp.json.template" ]; then
            actor_name=$(basename "$actor_dir")
            echo "- $actor_name: Actor CLI server"
        fi
    done
fi