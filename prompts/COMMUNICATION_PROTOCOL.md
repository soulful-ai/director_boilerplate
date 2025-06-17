# Communication Protocol

Director-Actor communication via shared workspace.

## Shared Workspace Structure

```
.shared-workspace/
├── tasks/          # Director → Actor
├── responses/      # Actor → Director
├── context/        # Shared state
└── logs/           # Activity logs
```

## Task Delegation

```bash
# Write task file
cat > .shared-workspace/tasks/coder-task.md << 'EOF'
---
actor: coder
priority: high
deadline: 2 hours
---
## Task: Implement user authentication

### Requirements
- OAuth2 integration
- Session management
- Test coverage > 80%

### Deliverables
- [ ] Implementation
- [ ] Tests
- [ ] Documentation
- [ ] Test environment link
EOF

# Start actor
npm run nx run workspace:start-actor --actor=coder
```

## Monitoring Responses

```bash
# Watch for status updates
tail -f .shared-workspace/responses/coder-status.md

# Check for challenges
watch -n 5 'cat .shared-workspace/responses/coder-challenges.md'

# Monitor logs
tail -f .shared-workspace/logs/coder-activity.log
```

## Response Formats

### Status Update
```markdown
STATUS: in_progress
PROGRESS: 45%
CURRENT: Implementing OAuth flow
NEXT: Add session management
ETA: 45 minutes
```

### Challenge Report
```markdown
CHALLENGE: Missing Google OAuth credentials
TYPE: environment_variable
REQUIRED: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
IMPACT: Cannot proceed with OAuth implementation
```

### Completion
```markdown
COMPLETED: User authentication
TEST_ENV: https://preview-auth.example.com
COVERAGE: 85%
NOTES: Ready for review
```