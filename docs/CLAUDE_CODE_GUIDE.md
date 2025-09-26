# Claude Code + RFD: The Complete Anti-Squirrel Guide

## 🎯 The Promise: You WILL Stay On Track

RFD enforces reality-based development through **concrete checkpoints** that cannot be faked. Here's how it prevents squirreling and keeps you focused:

### Anti-Squirrel Mechanisms

1. **Feature Lock**: You can ONLY work on features stored in database
2. **Validation Gates**: Can't proceed without passing validation
3. **Session Context**: Claude reads (never edits) `.rfd/context/current.md`
4. **Reality Checks**: Code must actually run - no theoretical progress
5. **Automatic Recovery**: Pick up exactly where you left off

## 🚀 Starting a New Claude Code Session

### What to Say to Claude (Copy & Paste This):

```
Continue work on the RFD project. Check the current session and continue the active feature. Use these commands:
1. rfd check - to see current status
2. rfd feature list - to see features from database
3. rfd session start <feature> - if no session active
4. rfd validate - to check progress
5. Remember: .rfd/context files are READ-ONLY
```

### Claude Will Automatically:
1. Read `CLAUDE.md` for instructions
2. Check `.rfd/context/current.md` for active session (READ-ONLY)
3. Use `rfd feature list` to see features from database
4. Read `.rfd/config.yaml` for project configuration
5. Continue exactly where you left off

## 📋 Complete Command Reference

### Session Management
```bash
# Start work on a feature
rfd session start user_auth

# Check current session
rfd check

# Show session status (NEW v5.0)
rfd session status

# End session (creates snapshot)
rfd session end

# View session history
rfd session list
```

### Development Workflow
```bash
# Build current feature
rfd build

# Validate against spec
rfd validate

# Save checkpoint (only if passing)
rfd checkpoint "Added login endpoint"

# Revert to last working state
rfd revert
```

### Specification Management
```bash
# Create new spec interactively
rfd spec create

# Review current spec
rfd spec review

# Generate comprehensive specs
rfd spec generate --type all
rfd spec generate --type constitution
rfd spec generate --type phases
rfd spec generate --type api
rfd spec generate --type guidelines
rfd spec generate --type adr

# Validate spec compliance
rfd spec validate
```

### Initialization Options
```bash
# Simple init
rfd init

# Interactive wizard (RECOMMENDED)
rfd init --wizard

# Import from PRD
rfd init --from-prd requirements.md

# For existing projects
rfd init --wizard --mode brownfield

# For exploration projects
rfd init --wizard --mode exploration
```

### Memory & Recovery
```bash
# Show AI memory
rfd memory show

# Reset memory (if corrupted)
rfd memory reset

# Sync with database
rfd sync

# Recovery from crash
rfd recover
```

### Project Management
```bash
# Update feature status
rfd feature update user_auth --status complete

# Add new feature
rfd feature add

# Show project metrics
rfd metrics

# Sync features with database
rfd project sync
```

## 🛡️ How RFD Prevents Squirreling

### 1. **Feature-Level Lock**
```yaml
# Database defines allowed features
features:
  - id: user_auth
    description: "User authentication"
    acceptance: "Users can login"
    status: building  # <-- You're locked to this
```

**What Happens If You Try to Squirrel:**
- `rfd validate` → ❌ "Feature not in spec"
- `rfd checkpoint` → ❌ "Cannot save - working on undefined feature"
- Claude gets reminder → "Stay on user_auth feature"

### 2. **Validation Requirements**
```yaml
rules:
  must_pass_tests: true
  no_mocks_in_prod: true
```

**Reality Enforcement:**
- Code MUST compile/run
- Tests MUST pass
- No fake data allowed
- API endpoints MUST respond

### 3. **Session Persistence**
```bash
# Monday: Start feature
rfd session start user_auth
# Work for 2 hours...
rfd checkpoint "Login endpoint working"

# Tuesday: Continue exactly where you left off
rfd check
> Session: user_auth (started Monday)
> Last checkpoint: "Login endpoint working"
> Next: Implement password reset
```

### 4. **Context Preservation**
Files that maintain context:
- `.rfd/context/current.md` - Active session details
- `.rfd/context/memory.json` - What worked/failed
- `.rfd/context/snapshots/` - Session history
- `.rfd/memory.db` - Database with features and progress

## 🔄 Session Recovery Scenarios

### Scenario 1: Claude Code Restart
```bash
# Claude Code restarts, you say:
"Continue the RFD session"

# Claude automatically:
1. Reads .rfd/context/current.md
2. Sees: "Working on user_auth, 3/5 tests passing"
3. Continues fixing the failing tests
```

### Scenario 2: Computer Crash
```bash
# After reboot:
rfd recover

# RFD:
1. Checks last checkpoint
2. Reverts to last working state
3. Shows exactly what you were doing
4. Resumes from safe point
```

### Scenario 3: Accidental Squirrel
```bash
# You went off-track and broke things:
rfd revert

# RFD:
1. Returns to last passing checkpoint
2. Shows what feature you should work on
3. Restores working code
```

### Scenario 4: New Day, Fresh Start
```bash
# Start your day:
rfd check

> Current Status:
> Feature: user_auth (70% complete)
> Last worked: yesterday 5pm
> Next task: Password reset endpoint
> Tests: 3/5 passing

# Continue:
rfd validate  # See what needs fixing
```

## ✅ Trust Verification

### How to Verify RFD is Working:

1. **Test the Lock:**
```bash
# Try to work on undefined feature
rfd session start random_feature
> ❌ Error: Feature 'random_feature' not found in database
```

2. **Test Reality Check:**
```bash
# Write broken code
echo "syntax error" > main.py
rfd checkpoint "Added feature"
> ❌ Error: Build failed - cannot checkpoint
```

3. **Test Recovery:**
```bash
# Mess things up
rm important_file.py
rfd revert
> ✅ Reverted to last checkpoint
# File is back!
```

4. **Test Session Persistence:**
```bash
# Morning session
rfd session start user_auth
# Do work...
rfd checkpoint "Morning work"

# Afternoon (new terminal)
rfd check
> Session: user_auth (active)
> Last checkpoint: "Morning work"
# Continues exactly where you left off
```

## 🚨 Red Flags That RFD Catches

1. **"I'll just quickly add this feature"** → ❌ Not in database
2. **"Let me refactor everything"** → ❌ Not current feature
3. **"This mock data is fine for now"** → ❌ no_mocks_in_prod
4. **"Tests can wait"** → ❌ must_pass_tests
5. **"I think I implemented this"** → ❌ Validation proves reality

## 📊 Metrics That Prove It Works

RFD tracks and shows:
```bash
rfd metrics

Drift Incidents: 0        # Times you went off track
Checkpoints: 47          # Successful saves
Reverts: 3               # Times you had to go back
Features Complete: 12/15  # Progress
Session Continuity: 98%   # Context preserved
```

## 🎮 Quick Start Challenge

Try this to prove RFD works:

1. **Initialize:**
```bash
rfd init --wizard
# Answer: "Test Project", add 1 feature
```

2. **Start Session:**
```bash
rfd session start test_feature
```

3. **Try to Squirrel:**
```bash
# Try to work on something else
echo "random code" > random.py
rfd checkpoint "Added random stuff"
# ❌ FAILS - not part of test_feature
```

4. **Do Real Work:**
```bash
# Work on actual feature
# Create code that matches acceptance criteria
rfd validate
# ✅ PASSES
rfd checkpoint "Feature complete"
```

5. **Simulate Crash:**
```bash
# Close terminal, reopen
rfd check
# Still shows test_feature active!
```

## 💡 Pro Tips

### For Maximum Focus:
1. Start each session with `rfd check`
2. Read the acceptance criteria from `rfd feature show <id>`
3. Only work on the active feature
4. Checkpoint every small success
5. End sessions properly with `rfd session end`

### For Claude Code:
1. ALWAYS start with: "Continue the RFD session"
2. Let Claude run `rfd check` first
3. Follow Claude's interpretation of current.md
4. Ask Claude to checkpoint after each success

### For Skeptics:
1. Try to break it - you'll see it catches everything
2. Check `.rfd/memory.db` - it's a real database
3. Look at `rfd dashboard` - shows progress from database
4. Review `.rfd/context/` - your entire history

## 🆘 When Things Go Wrong

### "I don't trust the current state"
```bash
rfd validate --full
# Shows EXACTLY what's real vs claimed
```

### "I think I lost work"
```bash
ls .rfd/context/snapshots/
# All your sessions are saved
rfd session restore <snapshot>
```

### "Claude is confused"
```bash
rfd memory reset
rfd check
# Fresh start with current reality
```

### "Everything is broken"
```bash
rfd revert
# Back to last known good state
```

## 🎯 The Bottom Line

**RFD makes squirreling impossible because:**
1. Features are locked in database
2. Progress requires passing validation
3. Context persists across sessions
4. Reality beats theory every time
5. Recovery is always possible

**You literally cannot:**
- Work on undefined features
- Claim false progress
- Lose context between sessions
- Get permanently stuck

**You literally must:**
- Follow the spec
- Write working code
- Pass validation
- Make real progress

---

## Ready to Trust It?

Start a new Claude Code session and say:
```
I have RFD installed. Run 'rfd check' and continue the current session. Follow the RFD workflow and keep me on track.
```

Claude will:
1. Check current status
2. Read the context
3. Continue your feature
4. Prevent any squirreling
5. Save real progress

**No faith required - RFD proves itself through reality validation.**