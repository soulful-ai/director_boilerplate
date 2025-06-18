# Director Boilerplate

## Purpose

Template for creating orchestrator systems that manage multiple specialized Claude actors. Provides task delegation, quality control, test environment deployment, and production release management through git submodule-based actor coordination.

## Important Note

**Actor Agnostic**: This template works with any type of specialized actors  
**Port Convention**: Director uses 9000, actors use 9001-9099  
**Communication**: Real-time shared workspace streaming  
**Environments**: Supports both local and GitHub Codespaces

## Folder Structure

```
/
├── apps/
│   └── mcp/
│       └── cli_use/          # Director MCP server (port 9000)
├── packages/                 # Actor submodules (added by organization)
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

1. **Clone repository:**
   ```bash
   git clone https://github.com/[your-org]/[your-director]
   cd [your-director]
   ```

2. **Setup environment:**
   ```bash
   ./scripts/setup-environment.sh
   ```

3. **Configure MCP:**
   ```bash
   cp .env.example .env
   # Edit .env with your paths and settings
   npx nx generate-mcp-config
   ```

## Start Development

```bash
# Quick start - Director only
npx nx run workspace:start-director

# Full orchestration system
npx nx run workspace:start-orchestration

# Individual actor CLIs (after adding actors)
npx nx run workspace:start-cli:[actor-name]    # Ports 9001+
```

## Adding Actors

### 1. Create Actor from Boilerplate

```bash
# Clone actor boilerplate
cd packages
git clone https://github.com/soulful-ai/boilerplate.git [actor-name]
cd [actor-name]

# Customize for your domain
git remote set-url origin https://github.com/[your-org]/[actor-name].git
# Edit CLAUDE.md, add specialized apps, update port assignment
```

### 2. Add as Submodule

```bash
# Add to director
git submodule add https://github.com/[your-org]/[actor-name] packages/[actor-name]

# Update orchestration config
# Add to project.json, scripts, and .env
```

### 3. Configure Communication

Update `.env` with actor paths:
```bash
[ACTOR_NAME]_ROOT=$WORKSPACE_ROOT/packages/[actor-name]
[ACTOR_NAME]_PORT=900X
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