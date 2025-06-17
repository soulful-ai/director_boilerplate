# Director Prompt Files

Concise, actionable guides for Director operations (max 100 lines each).

## Quick Reference

### Essential Commands
```bash
# Environment setup
./scripts/setup-environment.sh
source .env.detected

# Start Director
npm run nx run workspace:start-director

# Actor management
npm run nx run workspace:sync-submodules
npm run nx run workspace:start-actor --actor=[name]
```

### Task Delegation
```bash
# Write task to shared workspace
echo "Task content" > .shared-workspace/tasks/actor-task.md

# Monitor responses
tail -f .shared-workspace/responses/actor-status.md
```

### Challenge Escalation
```bash
# Report blocker
echo "CHALLENGE: Missing API key" >> .shared-workspace/responses/challenges.md

# Request user input
echo "NEEDS: User decision on architecture" >> .shared-workspace/responses/needs.md
```

## Available Guides

1. **[Environment Setup](ENVIRONMENT_SETUP.md)** - Configure for local/Codespaces
2. **[Orchestration Commands](ORCHESTRATION_COMMANDS.md)** - Core Director operations
3. **[Actor Management](ACTOR_MANAGEMENT.md)** - Add and manage actors
4. **[Communication Protocol](COMMUNICATION_PROTOCOL.md)** - Shared workspace patterns
5. **[Task Delegation](TASK_DELEGATION.md)** - Breaking down requests
6. **[Challenge Escalation](CHALLENGE_ESCALATION.md)** - Handling blockers
7. **[Test Deployment](TEST_DEPLOYMENT.md)** - Preview environments
8. **[Production Release](PRODUCTION_RELEASE.md)** - Deployment management
9. **[Quality Control](QUALITY_CONTROL.md)** - Review standards
10. **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues

## Best Practices

- Keep guides under 100 lines
- Focus on copy-paste commands
- Test all examples
- Update with learnings