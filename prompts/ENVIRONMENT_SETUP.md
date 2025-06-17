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

## Troubleshooting

```bash
# Missing workspace root
export WORKSPACE_ROOT=$(pwd)

# Permission denied
chmod +x scripts/*.sh

# Environment not loading
source .env.detected && source .env
```