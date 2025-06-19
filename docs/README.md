# PM Director Documentation Library

## Purpose

External documentation, tutorials, and guides discovered during PM Director operations. This supplements inline documentation with valuable resources found through curiosity-driven development.

## Structure

```
/docs
├── actor-communication/    # Actor communication patterns (existing)
├── nx/                    # Nx monorepo tooling guides
├── mcp/                   # Model Context Protocol documentation
├── telegram-auth/         # Telegram authentication patterns
├── ngrok/                 # Ngrok tunnel configuration
└── orchestration/         # PM Director orchestration patterns
```

## Documentation Strategy

### When to Add Documentation

Add documentation to this folder when:
- **Web searches reveal valuable tutorials** related to roadmap items
- **New best practices emerge** for technologies we use
- **Fresh documentation appears** for key dependencies (Nx, MCP, etc.)
- **Solutions to complex problems** are discovered online
- **Architectural patterns** prove useful for our use cases

### Documentation Workflow

1. **During Development**: When researching solutions, bookmark valuable resources
2. **After PR Success**: Update docs alongside changelog
3. **Version Everything**: Include version numbers and dates
4. **Link Sources**: Always include original URLs

### Example Entry

```markdown
# [Technology] [Topic]
Source: [URL]
Date: YYYY-MM-DD
Version: X.Y.Z (if applicable)

## Summary
Brief description of why this is valuable

## Key Points
- Important takeaways
- Practical applications
- Integration tips

## Code Examples
```

## Current Documentation

### External Resources
- `codespaces/` - GitHub Codespaces setup guides
- `ngrok/` - Ngrok tunnel configuration documentation

## Adding New Documentation

When you discover valuable resources:

```bash
# 1. Create category if needed
mkdir -p docs/[category]/[version]

# 2. Add documentation
cat > docs/[category]/[topic].md << EOF
# [Topic] Documentation
Source: [URL]
Date: $(date +%Y-%m-%d)
Version: [X.Y.Z]

## Why This Matters
[Explain relevance to PM Director/actors]

## Key Insights
[Main takeaways]

## Implementation Notes
[How to apply this knowledge]
EOF

# 3. Update this README's index
# 4. Commit with PR (never direct to main)
```

## Best Practices

1. **Be Selective**: Only add truly valuable, non-obvious documentation
2. **Stay Current**: Regularly review and update outdated docs
3. **Link to Code**: Reference where patterns are implemented
4. **Version Strictly**: Always note versions for framework-specific docs
5. **Credit Sources**: Include original URLs and authors

## Quick Reference Priority

When searching for solutions, check in this order:
1. This docs folder (for curated, tested solutions)
2. Actor-specific docs (packages/*/docs/)
3. Web search for latest information
4. Official documentation sites

Remember: This folder is our collective memory of valuable discoveries!