#!/usr/bin/env bash
# Start Director MCP server with public Codespace port forwarding

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Director Public MCP Server${NC}"

# Check if we're in a Codespace
if [ -z "$CODESPACE_NAME" ]; then
    echo -e "${RED}❌ Error: Not running in GitHub Codespaces${NC}"
    echo "This script is designed for GitHub Codespaces environments."
    echo "For local development, use: npx nx run mcp-cli_use:serve-sse"
    exit 1
fi

# Load environment variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

echo -e "${BLUE}📁 Loading environment from .env...${NC}"
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
else
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please run: cp .env.example .env && ./scripts/setup-environment.sh"
    exit 1
fi

# Kill any existing CLI servers
echo -e "${BLUE}🔧 Cleaning up existing servers...${NC}"
pkill -f "cli_use_server.*port 9000" 2>/dev/null || true
sleep 2

# Start the MCP server
echo -e "${BLUE}🔌 Starting MCP server on port 9000...${NC}"
cd "$PROJECT_ROOT"
nohup npx nx run mcp-cli_use:serve-sse > /tmp/director-public-server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
echo -e "${BLUE}⏳ Waiting for server to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:9000/sse >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Server started successfully${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Server failed to start. Check logs: tail -f /tmp/director-public-server.log${NC}"
        exit 1
    fi
    sleep 1
done

# Make port public
echo -e "${BLUE}🌐 Making port 9000 public...${NC}"
gh codespace ports visibility 9000:public --codespace "$CODESPACE_NAME" || {
    echo -e "${RED}❌ Failed to make port public${NC}"
    exit 1
}

# Get the public URL
PUBLIC_URL="https://${CODESPACE_NAME}-9000.app.github.dev/sse"

echo -e "${GREEN}✅ Director MCP Server is now publicly accessible!${NC}"
echo ""
echo -e "${BLUE}📋 Connection Details:${NC}"
echo -e "   Public URL: ${GREEN}${PUBLIC_URL}${NC}"
echo -e "   Transport: SSE (Server-Sent Events)"
echo -e "   Port: 9000"
echo -e "   Process ID: $SERVER_PID"
echo ""
echo -e "${BLUE}🔑 Authentication:${NC}"
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "   Telegram Auth: Configured"
    echo -e "   Allowed Users: $(grep TELEGRAM_ALLOWED_USERS "$PROJECT_ROOT/.env" | cut -d'=' -f2)"
fi
echo ""
echo -e "${BLUE}📊 Monitoring:${NC}"
echo -e "   Logs: tail -f /tmp/director-public-server.log"
echo -e "   Stop: kill $SERVER_PID"
echo ""
echo -e "${GREEN}🎉 Ready to connect from Claude Desktop!${NC}"

# Exit successfully (server continues in background)
exit 0