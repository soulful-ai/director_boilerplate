# Codespace & Browser Management

## PM Director's Infrastructure Responsibilities

The PM Director manages all codespace operations and browser-based interactions as the primary orchestrator.

## Codespace Management

### Current Codespace
Update these values when setting up a new workspace:
- **Codespace Name**: `[your-codespace-name]`
- **Base URL**: `https://[your-codespace-name].github.dev/`
- **Port Forwarding Pattern**: `https://[your-codespace-name]-<PORT>.app.github.dev`

### Codespace Commands
```bash
# List codespaces
gh cs list --json name,state

# Stop current codespace
gh codespace stop --codespace [your-codespace-name]

# Port visibility management
gh codespace ports visibility <port>:public --codespace [your-codespace-name]

# Examples
gh codespace ports visibility 9000:public --codespace [your-codespace-name]
gh codespace ports visibility 3000:public --codespace [your-codespace-name]
```

### Port Allocations
- **9000**: PM Director CLI (MCP SSE endpoint)
- **9001**: First Actor services
- **9002**: Second Actor services
- **9003**: Third Actor services
- **9004**: Fourth Actor services

## Browser Management

### Opening Test Environments
```bash
# Open URLs in browser (PM responsibility)
sensible-browser <url>

# Test environment URLs
sensible-browser https://[your-codespace-name]-3000.app.github.dev
sensible-browser https://[your-codespace-name]-3100.app.github.dev

# Open without blocking terminal
sensible-browser <url> &
```

### Authentication Flows
```bash
# GitHub authentication
gh auth login

# Other authentication flows based on your needs
sensible-browser https://accounts.google.com/oauth/authorize
```

## Test Environment Deployment Workflow

1. **PM Director delegates** deployment to appropriate Actor
2. **Actor deploys** and reports URL
3. **PM Director opens** the URL for user verification
4. **PM Director reports** to user with test link

## Environment Detection

```bash
# Check if in Codespace
if [[ -n "$CODESPACE_NAME" ]]; then
    echo "In GitHub Codespace: $CODESPACE_NAME"
    BASE_URL="https://${CODESPACE_NAME}.github.dev"
else
    echo "Local development environment"
    BASE_URL="http://localhost"
fi
```

## Best Practices

1. **Always verify port visibility** before sharing URLs
2. **Use background processes** (`&`) for browser commands
3. **Track all open ports** in documentation
4. **Shutdown codespaces** when not in use to save resources
5. **Update codespace references** when switching instances

## Quick Reference

```bash
# PM Director MCP endpoint (port 9000)
https://[your-codespace-name]-9000.app.github.dev/sse

# Stop codespace when done
gh codespace stop --codespace [your-codespace-name]
```