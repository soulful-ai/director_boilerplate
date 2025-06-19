# Environment Setup

Configure Director for local development or GitHub Codespaces.

## Quick Setup

```bash
# 1. Run setup script
./scripts/setup-environment.sh

# 2. Source environment
source .env.detected

# 3. Verify setup
echo $WORKSPACE_ROOT
```

## Environment Detection

### GitHub Codespaces
```bash
# Auto-detected when CODESPACE_NAME exists
# Workspace root: /workspaces/workspace
```

### Local Development
```bash
# Searches for CLAUDE.md to find workspace root
# Falls back to current directory
```

## Configuration Files

### .env.detected (auto-generated)
```bash
ENV_TYPE=local|codespace
WORKSPACE_ROOT=/path/to/workspace
DIRECTOR_PORT=9000
```

### .env (user configuration)
```bash
# Copy from .env.example
cp .env.example .env

# Add credentials
TELEGRAM_BOT_TOKEN=your_token
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

## Actor Path Configuration

```bash
# Added automatically when actors exist
CODER_ROOT=$WORKSPACE_ROOT/packages/coder
CODER_PORT=9001
```

## MCP (Model Context Protocol) Setup

### Quick MCP Setup
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env to set WORKSPACE_ROOT
# For Codespaces: WORKSPACE_ROOT=/workspaces/workspace
# For local: WORKSPACE_ROOT=/path/to/your/workspace

# 3. Source the environment
source .env

# 4. Generate MCP configuration
npx nx run workspace:generate-mcp-config

# 5. Verify generation (check parent directory)
ls -la ../.mcp.json

# 6. Restart Claude to pick up new MCP configuration
```

### MCP Configuration Details
- **Template**: `.mcp.json.template` defines MCP server configuration
- **Output**: `../.mcp.json` (at workspace root for Claude access)
- **Purpose**: Enables Claude to use CLI tools via MCP protocol
- **Security**: Configured via ALLOWED_COMMANDS and ALLOWED_FLAGS in .env

## Troubleshooting

```bash
# Missing workspace root
export WORKSPACE_ROOT=$(pwd)

# Permission denied
chmod +x scripts/*.sh

# Environment not loading
source .env.detected && source .env

# MCP config not generating
# Check .env has required vars:
grep -E "(MCP_CLI_DIR|ALLOWED_DIR)" .env

# Claude not finding MCP config
# Ensure it's at workspace root:
ls -la $WORKSPACE_ROOT/.mcp.json
```