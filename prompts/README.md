# Director Prompts Documentation

Concise, actionable guides for Director operations. Each file is limited to 100 lines for quick access.

## Available Prompts

### Core Documentation
- **[README.md](README.md)** - This index file listing all prompts
- **[ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)** - Dual environment configuration and MCP setup
- **[ACTOR_MANAGEMENT.md](ACTOR_MANAGEMENT.md)** - Git submodule patterns for actors
- **[COMMUNICATION_PROTOCOL.md](COMMUNICATION_PROTOCOL.md)** - Shared workspace patterns
- **[CODESPACE_BROWSER_MANAGEMENT.md](CODESPACE_BROWSER_MANAGEMENT.md)** - Browser and port management

## Quick Start

### 1. Environment Setup
```bash
# Auto-detect environment (local vs Codespaces)
./scripts/setup-environment.sh

# Configure environment
cp .env.example .env
vi .env  # Set WORKSPACE_ROOT
```

### 2. Generate MCP Configuration
```bash
# Generate .mcp.json at workspace root
npx nx run workspace:generate-mcp-config

# Restart Claude to pick up configuration
```

### 3. Start Orchestration
```bash
# Start Director MCP server
npx nx serve

# Or start full orchestration
npx nx run workspace:start-orchestration
```

## Actor Management

### Add New Actor
```bash
# Add as git submodule
git submodule add https://github.com/[org]/[actor] [actor-name]

# Configure in .env
echo "[ACTOR]_ROOT=\$WORKSPACE_ROOT/[actor-name]" >> .env
echo "[ACTOR]_PORT=900X" >> .env
```

### Delegate Tasks
```bash
# Write task
cat > .shared-workspace/tasks/current.md << EOF
Task for [Actor]: Implement [feature]
Requirements: [details]
EOF

# Start actor
npx nx run workspace:start-actor --actor=[name]
```

## Communication Patterns

### Monitor Progress
```bash
# Watch actor responses
tail -f .shared-workspace/responses/status.md

# Check for challenges
watch -n 1 cat .shared-workspace/responses/challenges.md
```

### Escalate to User
```bash
# Request decision
echo "@User: Need decision on [topic]" >> .shared-workspace/responses/needs.md

# Report blocker
echo "BLOCKED: [Actor] needs [resource]" >> .shared-workspace/responses/blockers.md
```

## Best Practices

1. **Test environments first** - Deploy preview before production
2. **Immediate escalation** - Don't wait on blockers
3. **Clear delegation** - Specific requirements for actors
4. **Monitor quality** - Review actor outputs
5. **User collaboration** - Frequent check-ins

## Directory Structure
```
director/
├── prompts/          # These documentation files
├── scripts/          # Automation tools
├── apps/mcp/         # MCP server implementation
└── .env              # Configuration (gitignored)
```

Remember: Orchestrate, don't implement. Delegate to actors!