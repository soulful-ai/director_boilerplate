# Director Boilerplate

A production-ready template for creating AI orchestration systems that coordinate multiple specialized Claude actors. This boilerplate provides the foundation for building complex AI systems with proper task delegation, quality control, and deployment management.

## Key Features

- **Multi-Actor Orchestration**: Coordinate multiple specialized AI actors via git submodules
- **MCP Protocol Support**: Built-in Model Context Protocol server for Claude integration
- **Flexible Architecture**: Supports both flat and nested workspace structures
- **Environment Agnostic**: Works seamlessly in local development and GitHub Codespaces
- **Security First**: Configurable command restrictions and authentication support
- **Production Ready**: Includes CI/CD patterns, testing framework, and deployment guides

## Folder Structure

```
/
├── apps/
│   └── mcp/
│       └── cli_use/          # Director MCP server (port 9000)
├── packages/                 # Actor submodules (optional - for nested structure)
├── prompts/                  # Actionable workflow guides
├── scripts/                  # Orchestration automation
├── libs/                     # Shared libraries
├── tools/                    # Director utilities
└── .shared-workspace/        # Inter-actor communication
```

## Prerequisites

- **Node.js** (v18 or higher)
- **Git** (for submodule management)
- **Python** (3.8+) and **uv** (for MCP servers)
- **Claude Code** (for actor delegation)
- **GitHub CLI** (`gh` for PR/issue management)

## Installation

1. **Create from template:**
   ```bash
   # Clone the boilerplate
   git clone https://github.com/soulful-ai/director_boilerplate my-director
   cd my-director
   
   # Remove boilerplate history and initialize your own
   rm -rf .git
   git init
   git add .
   git commit -m "Initial commit from director_boilerplate"
   ```

2. **Setup environment:**
   ```bash
   ./scripts/setup-environment.sh
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your specific settings
   ./scripts/generate-mcp-config.sh
   ```

## Start Development

```bash
# Quick start - Director only
npx nx run workspace:start-director

# Full orchestration system
npx nx run director:start-orchestration

# Individual actor CLIs (after adding actors)
npx nx run director:start-actor --actor=[actor-name]
```

## Adding Actors

### 1. Create Actor from Boilerplate

```bash
# For flat structure (recommended)
cd ..
git clone https://github.com/soulful-ai/actor_boilerplate my-actor
cd my-actor

# For nested structure
# mkdir -p packages
# cd packages
# git clone https://github.com/soulful-ai/actor_boilerplate my-actor
# cd my-actor

# Initialize as your own repository
rm -rf .git
git init
# Customize CLAUDE.md, add domain-specific apps, set port (900X)
```

### 2. Add as Submodule

```bash
# For flat structure (recommended)
cd path/to/director
git submodule add https://github.com/[your-org]/my-actor ../my-actor

# For nested structure
# git submodule add https://github.com/[your-org]/my-actor packages/my-actor

# Update director configuration
# Add actor to .env and project.json
```

### 3. Configure Communication

Update `.env` with actor configuration:
```bash
# For flat structure
MY_ACTOR_ROOT=$WORKSPACE_ROOT/../my-actor
MY_ACTOR_PORT=9001

# For nested structure
# MY_ACTOR_ROOT=$WORKSPACE_ROOT/packages/my-actor
# MY_ACTOR_PORT=9001
```

## Key Patterns

### Task Delegation Flow
1. **Receive Request** → Analyze and identify requirements
2. **Check Dependencies** → Identify missing credentials/config
3. **Escalate Blockers** → Immediately surface to user
4. **Delegate to Actor** → Write task to shared workspace
5. **Monitor Progress** → Real-time status tracking
6. **Deploy Test Env** → Provide preview links
7. **Production Release** → After user approval

### Communication Protocol
```
.shared-workspace/
├── tasks/          # Delegated tasks
├── responses/      # Actor updates
├── context/        # Shared state
└── logs/           # Activity logs
```

### Port Strategy
- **Director**: 9000 (MCP server)
- **Actors**: 9001-9099 (assigned sequentially)
- **Services**: Actor-specific (8000-8999)

## Common Commands

```bash
# Director operations
npx nx run workspace:start-director          # Start director only
npx nx run workspace:setup-workspace         # Initialize shared workspace
npx nx list                                  # Available generators
npx nx graph                                 # Project dependencies

# Actor management
npx nx run workspace:sync-submodules         # Initialize all actors
npx nx run workspace:update-actors           # Update all to latest
npx nx run workspace:start-actor --actor=[name]  # Start specific actor

# Development
npx nx run workspace:test                    # Run tests
npx nx run workspace:lint                    # Lint code
npx nx run workspace:build                   # Build all
```

## Customization Guide

### 1. Define Your Domain
- Update CLAUDE.md with director's specialization
- Define actor types needed for your domain
- Plan task delegation patterns

### 2. Create Specialized Actors
- Use actor boilerplate as starting point
- Add domain-specific applications
- Define clear actor boundaries

### 3. Implement Workflows
- Create prompt files for common procedures
- Define escalation patterns
- Document best practices

### 4. Scale Operations
- Add actors as needed
- Maintain clear documentation
- Update boilerplate with learnings

## Best Practices

### Documentation
- Maintain cascading README structure
- Keep CLAUDE.md under 40k chars
- Extract procedures to prompts/
- Test all command examples

### Actor Management
- One actor per domain expertise
- Clear responsibility boundaries
- Independent operation capability
- Consistent communication patterns

### Quality Control
- Review all actor outputs
- Validate test environments
- Ensure comprehensive testing
- Document deployment procedures

## Troubleshooting

### Quick Diagnostics
```bash
# Verify environment
echo $WORKSPACE_ROOT
source .env.detected

# Check actor status
npx nx run workspace:submodules:status

# Test shared workspace
npx nx run workspace:setup-workspace
```

### Common Issues
- **Path errors**: Run `./scripts/setup-environment.sh`
- **Actor not responding**: Check submodule initialization
- **Port conflicts**: Verify port assignments in .env
- **Permission denied**: Check script execution permissions

## Contributing

This boilerplate is maintained through active director development:
1. Implement improvements in your director
2. Backport general patterns to boilerplate
3. Submit PRs with tested enhancements
4. Keep actor-agnostic and domain-neutral

## Future Roadmap

- [ ] Nx plugin generator conversion
- [ ] Automated actor discovery
- [ ] Enhanced monitoring dashboard
- [ ] Multi-director coordination
- [ ] Cloud deployment templates