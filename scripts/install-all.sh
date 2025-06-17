#!/bin/bash

# Install all dependencies for Director Boilerplate

echo "📦 Installing Director Boilerplate dependencies..."

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Install Python dependencies for MCP server
if [ -d "apps/mcp/cli_use" ]; then
    echo "🐍 Installing Python dependencies for MCP server..."
    cd apps/mcp/cli_use
    if command -v uv &> /dev/null; then
        uv venv --allow-existing
        uv pip install --editable .
    else
        echo "⚠️  uv not found. Install with: pip install uv"
    fi
    cd ../../..
fi

# Initialize git submodules if any exist
if [ -f ".gitmodules" ]; then
    echo "📦 Initializing git submodules..."
    git submodule update --init --recursive
fi

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Run: ./scripts/setup-environment.sh"
echo "2. Configure .env file"
echo "3. Start director: npm run nx run workspace:start-director"