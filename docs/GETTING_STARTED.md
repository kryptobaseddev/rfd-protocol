# Getting Started with RFD Protocol

## What is RFD?

RFD (Reality-First Development) is a protocol that **prevents AI hallucination** and **eliminates squirrel-brain** in software development. It enforces concrete reality checkpoints that ensure you:
- Stay focused on defined features
- Can't claim false progress
- Always know where you left off
- Can recover from any situation

## Quick Start (5 Minutes)

### 1. Install RFD
```bash
pip install rfd-protocol
```

### 2. Initialize Your Project
```bash
# For new projects (RECOMMENDED)
rfd init --wizard

# For existing projects
rfd init --wizard --mode brownfield

# From requirements document
rfd init --from-prd requirements.md
```

### 3. Start Your First Session
```bash
# See available features
rfd feature list

# Start working on a feature
rfd session start hello_world

# Check your status anytime
rfd check
```

### 4. Develop with Reality Validation
```bash
# Write your code...

# Build it
rfd build

# Validate it works
rfd validate

# Save checkpoint if passing
rfd checkpoint "Hello world working"
```

### 5. End Your Session
```bash
# Creates recovery snapshot
rfd session end
```

## Complete First Project Tutorial

Let's build a real project from scratch to see how RFD keeps you on track:

### Step 1: Create Project with Wizard

```bash
rfd init --wizard
```

You'll be asked:
```
🚀 RFD Protocol Initialization Wizard

Project type:
> New project (Greenfield)    # Choose this
  Existing project (Brownfield)
  Research/Exploration project
  Import from PRD document

Project name: todo-api
Project description: Simple TODO API with authentication
```

Continue answering the wizard questions:
- Add 2-3 goals
- Add 3-5 requirements  
- Define 1-2 initial features
- Accept generation of full specs

### Step 2: Review Generated Specifications

The wizard created comprehensive specs for you:

```bash
ls specs/
# CONSTITUTION.md      - Project principles
# PHASES.md           - Development phases  
# API_CONTRACT.md     - API endpoints
# GUIDELINES.md       - Coding standards
# ADR-001-tech.md     - Tech decisions
```

Review your project structure:
```bash
rfd spec review
```

### Step 3: Start First Development Session

```bash
# See your features
rfd feature list
# ⭕ health_check - Basic health endpoint
# ⭕ user_auth - User authentication

# Start with the simplest
rfd session start health_check
```

RFD creates `.rfd/context/current.md` with your exact task.

### Step 4: Implement the Feature

Create your API file (example for Python/FastAPI):

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2024-01-15T10:00:00"}
```

### Step 5: Validate Your Work

```bash
# Build the project
rfd build
# ✅ Build successful!

# Validate against spec
rfd validate
# ✅ feature_health_check: GET /health returns 200
# Overall: ✅ PASSING

# Save checkpoint
rfd checkpoint "Health check endpoint working"
# ✅ Checkpoint saved
```

### Step 6: Complete the Feature

```bash
# Mark feature complete
rfd feature update health_check --status complete

# End session
rfd session end
# Session snapshot created
```

### Step 7: Start Next Day

```bash
# Next day, check where you left off
rfd check

# Output:
# 📦 Features:
#   ✅ health_check (1 checkpoint)
#   ⭕ user_auth (0 checkpoints)
# → Next: rfd session start user_auth

# Continue with next feature
rfd session start user_auth
```

## Working with Claude Code

### Starting a Claude Session

Open Claude Code and say:
```
I'm working on an RFD project. Please run 'rfd check' and continue the current session. Follow the RFD workflow.
```

### What Claude Will Do

1. **Check Status**: Run `rfd check`
2. **Read Context**: Review `.rfd/context/current.md`
3. **Follow Spec**: Read acceptance criteria from PROJECT.md
4. **Validate Work**: Run `rfd validate` after changes
5. **Save Progress**: Run `rfd checkpoint` when working

### Example Claude Conversation

You: "Continue the RFD session"

Claude: 
```bash
rfd check
# Session: user_auth (active)
# Next: Implement login endpoint

# I'll implement the login endpoint according to the spec...
[writes code]

rfd validate
# ✅ Validation passing

rfd checkpoint "Login endpoint implemented"
```

## PROJECT.md Configuration

### Understanding PROJECT.md Structure

Your PROJECT.md defines everything about your project:

```yaml
---
# REQUIRED FIELDS
name: "Your Project"
description: "What it does"
version: "0.1.0"

# TECHNOLOGY STACK (extensible)
stack:
  language: python           # Required
  framework: fastapi        # Required
  database: postgresql      # Required
  runtime: python-3.11      # Optional
  package_manager: pip      # Optional
  test_framework: pytest    # Optional
  deployment: docker        # Optional

# VALIDATION RULES
rules:
  max_files: 50
  max_loc_per_file: 500
  must_pass_tests: true
  no_mocks_in_prod: true
  min_test_coverage: 80     # Optional
  
# FEATURES (your work items)
features:
  - id: feature_1
    description: "What this feature does"
    acceptance: "How to verify it works"
    status: pending
    priority: high          # Optional
    depends_on: []          # Optional
---
```

### Customizing Rules

Edit PROJECT.md to adjust limits:

```yaml
rules:
  max_files: 100           # Increase file limit
  max_loc_per_file: 1000   # Allow longer files
  min_test_coverage: 90    # Require 90% coverage
  require_types: true      # Enforce type hints
```

### Adding Features

```bash
# Interactive
rfd feature add

# Or edit PROJECT.md directly:
features:
  - id: new_feature
    description: "New functionality"
    acceptance: "Tests pass"
    status: pending
```

## Common Scenarios

### Scenario: "I Lost Track of What I'm Doing"

```bash
rfd check
# Shows current session, feature, next action

cat .rfd/context/current.md
# Detailed session context

rfd memory show
# What worked/failed before
```

### Scenario: "I Went Off Track and Broke Things"

```bash
# See what's broken
rfd validate --verbose

# Revert to last working state
rfd revert

# Continue from safe point
rfd check
```

### Scenario: "Starting Fresh After Weekend"

```bash
# Monday morning
rfd check
# Shows exactly where you left off Friday

# Review progress
cat PROGRESS.md

# Continue
rfd session start <feature>
```

### Scenario: "AI Claims It Did Something"

```bash
# Verify the claim
rfd validate

# If failing:
# ❌ Feature not implemented
# ❌ Tests not passing
# AI hallucination detected!
```

### Scenario: "Want to Add Unplanned Feature"

```bash
# Try to work on it
rfd session start random_feature
# ❌ Error: Feature 'random_feature' not in PROJECT.md

# Proper way:
rfd feature add
# Add it to spec first
rfd session start new_feature
# Now you can work on it
```

## Best Practices

### 1. Start Each Day with Status Check
```bash
rfd check
rfd validate
# Know exactly where you are
```

### 2. Checkpoint Frequently
```bash
# After each small success
rfd checkpoint "Added user model"
rfd checkpoint "Database connection working"
rfd checkpoint "Tests passing"
```

### 3. Keep Features Small
```yaml
# Good: Specific and testable
features:
  - id: user_login
    acceptance: "POST /login returns JWT token"

# Bad: Too vague
features:
  - id: authentication
    acceptance: "Users can authenticate"
```

### 4. End Sessions Properly
```bash
# Creates snapshot for recovery
rfd session end

# Don't just close terminal!
```

### 5. Trust Validation Over Memory
```bash
# Don't trust: "I think I implemented that"
# Do trust:
rfd validate
# ✅ Reality confirmed
```

## Troubleshooting

### "Can't Start Session"
```bash
# Feature must exist in PROJECT.md
rfd feature list         # See available
rfd feature add          # Add new one
```

### "Validation Keeps Failing"
```bash
rfd validate --verbose   # See details
rfd spec review         # Check requirements
cat .rfd/context/current.md  # Current task
```

### "Lost All Context"
```bash
rfd recover             # Auto-recovery
ls .rfd/context/snapshots/  # Find snapshots
rfd session restore <id>    # Restore specific
```

### "Want to Start Over"
```bash
rfd memory reset        # Clear memory
rfd revert             # Go to last checkpoint
# Or completely fresh:
rm -rf .rfd PROJECT.md PROGRESS.md
rfd init --wizard
```

## Next Steps

1. **Read Full Documentation**
   - [CLI Reference](CLI_REFERENCE.md) - All commands
   - [PROJECT.md Schema](PROJECT_SCHEMA.md) - Configuration
   - [Claude Code Guide](CLAUDE_CODE_GUIDE.md) - AI integration

2. **Try Advanced Features**
   ```bash
   rfd spec generate --type all  # Generate all specs
   rfd metrics                   # See progress metrics
   rfd project sync             # Sync PROJECT.md with database
   ```

3. **Join Community**
   - Report issues: https://github.com/kryptobaseddev/rfd-protocol/issues
   - Share experiences
   - Contribute improvements

## The RFD Promise

With RFD, you will:
- ✅ Stay focused on defined features
- ✅ Make real, validated progress
- ✅ Never lose context between sessions
- ✅ Always be able to recover
- ✅ Ship working code, not theories

No faith required - RFD proves itself through reality validation.