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
npx nx run director:setup-workspace

# Function to start Director CLI
start_director() {
    echo ""
    echo "🎯 Starting Director CLI on port ${DIRECTOR_PORT:-9000}..."
    
    # Check if cli_use exists
    if [ ! -d "apps/mcp/cli_use" ]; then
        echo "❌ Director CLI not found at apps/mcp/cli_use"
        echo "📝 Please ensure the MCP server is properly set up"
        return 1
    fi
    
    # Start the Director MCP server
    cd apps/mcp/cli_use
    if [ -f "pyproject.toml" ]; then
        echo "Starting Python-based CLI server..."
        uv run cli_use &
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
    
    # Check for flat structure first
    if [ -f "../CLAUDE.md" ]; then
        for actor_dir in ../*/; do
            if [ -d "$actor_dir" ] && [ "$actor_dir" != "../$(basename $PWD)/" ]; then
                actor_name=$(basename "$actor_dir")
                # Skip boilerplates and check for project.json
                if [[ ! "$actor_name" =~ _boilerplate$ ]] && [ -f "$actor_dir/project.json" ]; then
                    echo "  - $actor_name (flat structure)"
                fi
            fi
        done
    # Then check nested structure
    elif [ -d "packages" ]; then
        for actor_dir in packages/*/; do
            if [ -d "$actor_dir" ]; then
                actor_name=$(basename "$actor_dir")
                echo "  - $actor_name (nested structure)"
            fi
        done
    else
        echo "  No actors found. Add actors as git submodules"
    fi
}

# Function to start specific actor
start_actor() {
    local actor_name=$1
    local actor_dir=""
    
    # Check flat structure first
    if [ -f "../CLAUDE.md" ] && [ -d "../$actor_name" ]; then
        actor_dir="../$actor_name"
    # Then check nested structure
    elif [ -d "packages/$actor_name" ]; then
        actor_dir="packages/$actor_name"
    else
        echo "❌ Actor '$actor_name' not found"
        return 1
    fi
    
    echo "🎭 Starting actor: $actor_name"
    cd "$actor_dir"
    
    # Start actor's MCP server
    if [ -f "package.json" ]; then
        npx nx serve &
        echo "✅ Actor $actor_name started"
    else
        echo "❌ Actor configuration not found"
    fi
    
    cd - > /dev/null
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
echo "  - Start specific actor: npx nx run director:start-actor --actor=[name]"
echo "  - Update all actors: npx nx run director:update-actors"
echo "  - Check status: npx nx run director:submodules:status"
echo ""
echo "🔗 Director CLI available at: http://localhost:${DIRECTOR_PORT:-9000}/sse"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running
wait