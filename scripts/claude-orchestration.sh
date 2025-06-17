#!/bin/bash

# Director Orchestration Script
# Manages the startup and coordination of Director and Actor Claude instances

echo "🚀 Starting Director Orchestration System..."

# Load environment
if [ -f .env.detected ]; then
    source .env.detected
fi

if [ -f .env ]; then
    source .env
fi

# Ensure workspace is set up
echo "📁 Setting up shared workspace..."
npm run nx run workspace:setup-workspace

# Function to start Director CLI
start_director() {
    echo ""
    echo "🎯 Starting Director CLI on port ${DIRECTOR_PORT:-9000}..."
    
    # Check if cli_use exists
    if [ ! -d "apps/mcp/cli_use" ]; then
        echo "⚠️  Director CLI not found. Creating from template..."
        # In real usage, this would be copied from actor_boilerplate
        mkdir -p apps/mcp/cli_use
        echo "📝 TODO: Copy CLI implementation from actor_boilerplate"
    fi
    
    # Start the Director MCP server
    cd apps/mcp/cli_use
    if [ -f "pyproject.toml" ]; then
        echo "Starting Python-based CLI server..."
        uv run mcp-server --port ${DIRECTOR_PORT:-9000} &
        DIRECTOR_PID=$!
        echo "✅ Director CLI started (PID: $DIRECTOR_PID)"
    else
        echo "❌ CLI server implementation not found"
    fi
    cd ../../..
}

# Function to list available actors
list_actors() {
    echo ""
    echo "📦 Available actors:"
    
    if [ -d "packages" ]; then
        for actor_dir in packages/*/; do
            if [ -d "$actor_dir" ]; then
                actor_name=$(basename "$actor_dir")
                echo "  - $actor_name"
            fi
        done
    else
        echo "  No actors found. Add actors as git submodules in packages/"
    fi
}

# Function to start specific actor
start_actor() {
    local actor_name=$1
    local actor_dir="packages/$actor_name"
    
    if [ ! -d "$actor_dir" ]; then
        echo "❌ Actor '$actor_name' not found in packages/"
        return 1
    fi
    
    echo "🎭 Starting actor: $actor_name"
    cd "$actor_dir"
    
    # Check for actor's start command
    if [ -f "package.json" ]; then
        npm run nx run mcp-cli_use:serve-sse &
        echo "✅ Actor $actor_name started"
    else
        echo "❌ Actor start configuration not found"
    fi
    
    cd ../..
}

# Main orchestration flow
echo ""
echo "================================"
echo "Director Orchestration System"
echo "================================"
echo ""

# Start Director
start_director

# List available actors
list_actors

# Instructions
echo ""
echo "📖 Orchestration Commands:"
echo "  - Start specific actor: npm run nx run workspace:start-actor --actor=[name]"
echo "  - Update all actors: npm run nx run workspace:update-actors"
echo "  - Check status: npm run nx run workspace:submodules:status"
echo ""
echo "🔗 Director CLI available at: http://localhost:${DIRECTOR_PORT:-9000}/sse"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running
wait