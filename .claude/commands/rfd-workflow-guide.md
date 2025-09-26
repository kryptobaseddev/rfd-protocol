---
description: Complete guide to using RFD workflow commands effectively
allowed-tools: Bash(*), Read(.rfd/config.yaml), TodoWrite
---

# RFD Workflow Guide - How to Use RFD Properly

## Starting a New Session (Not Just /rfd-resume!)

### Option 1: Workflow-Enforced Development (RECOMMENDED)
```bash
rfd workflow start <feature-id>
```
This enforces spec-driven development with gates and prevents deviation.

### Option 2: Isolated Git Worktree Session
```bash
rfd session start <feature-id> --isolate
```
Creates a separate git worktree for the feature - clean isolation.

### Option 3: Regular Session
```bash
rfd session start <feature-id>
```
Standard session without isolation.

## During Development

### Core Commands You Should Use:
```bash
rfd check           # Quick health check before changes
rfd validate        # Validate implementation against specs
rfd checkpoint      # Save working state
rfd build          # Build current feature
rfd audit          # Check database-first compliance
```

### Gap-Aware Commands:
```bash
rfd gaps           # See what's missing in the system
rfd analyze        # Cross-artifact validation
rfd workflow status # Check workflow enforcement
```

### When Things Break:
```bash
rfd revert         # Go back to last working checkpoint
rfd migrate        # Apply any pending migrations
rfd upgrade-check  # Check if RFD itself needs updating
```

## Workflow Enforcement (Prevents Deviation)

### Start with Enforcement:
```bash
rfd workflow start <feature-id>
```

### When Blocked:
```bash
rfd workflow query "What's blocking me"
rfd workflow status  # See current state and queries
```

### To Proceed:
```bash
rfd workflow proceed  # Try to move to next phase
```

### Resolve Issues:
```bash
rfd workflow resolve <query-id> "How I fixed it"
```

## Session Management Best Practices

1. **Always Start Fresh:**
   ```bash
   rfd check
   rfd gaps
   rfd session status
   ```

2. **Use Workflow for New Features:**
   ```bash
   rfd workflow start <feature>  # NOT just session start
   ```

3. **Track Progress:**
   ```bash
   rfd dashboard
   rfd validate
   rfd checkpoint "What I accomplished"
   ```

4. **End Properly:**
   ```bash
   rfd session end  # Cleans up, updates context
   ```

## What /rfd-resume Should Really Do

Instead of just `/rfd-resume`, use this sequence:
1. `rfd check` - System health
2. `rfd gaps` - See what's missing
3. `rfd session status` - Current work
4. `rfd workflow status` - Any blocked items
5. Then decide: continue session or start new workflow

## Common Mistakes to Avoid

❌ Only using `/rfd-resume` every session
❌ Not checking gaps regularly
❌ Skipping `rfd workflow` for new features
❌ Not using `rfd checkpoint` to save progress
❌ Ignoring `rfd audit` warnings

✅ Use the full command set
✅ Track gaps actively
✅ Enforce workflows on new work
✅ Checkpoint frequently
✅ Address audit issues immediately