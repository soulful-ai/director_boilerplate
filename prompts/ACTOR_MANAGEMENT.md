# Actor Management

Add and manage specialized actors via git submodules.

## Adding New Actor

```bash
# 1. Create from boilerplate
cd packages
git clone https://github.com/soulful-ai/boilerplate.git my-actor
cd my-actor

# 2. Customize actor
# - Edit CLAUDE.md for specialization
# - Add domain-specific apps
# - Update port assignment (900X)

# 3. Push to GitHub
git remote set-url origin https://github.com/[org]/my-actor.git
git push -u origin main
cd ../..

# 4. Add as submodule
git submodule add https://github.com/[org]/my-actor packages/my-actor

# 5. Configure in .env
echo "MY_ACTOR_ROOT=\$WORKSPACE_ROOT/packages/my-actor" >> .env
echo "MY_ACTOR_PORT=9002" >> .env
```

## Common Operations

```bash
# Initialize all actors
npx nx run workspace:sync-submodules

# Update all actors
npx nx run workspace:update-actors

# Check status
npx nx run workspace:submodules:status

# Start specific actor
npx nx run workspace:start-actor --actor=my-actor
```

## Port Assignment

```
Director: 9000
Actor 1: 9001
Actor 2: 9002
...
Actor N: 900N
```

## Removing Actor

```bash
# Remove submodule
git submodule deinit packages/actor-name
git rm packages/actor-name
rm -rf .git/modules/packages/actor-name

# Remove from .env
# Manual edit required
```