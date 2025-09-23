# RFD CLI Complete Reference

## Installation

```bash
# Install from PyPI
pip install rfd-protocol

# Upgrade to latest
pip install --upgrade rfd-protocol

# Install from source
git clone https://github.com/kryptobaseddev/rfd-protocol.git
cd rfd-protocol
pip install -e .
```

## Command Structure

```
rfd [OPTIONS] COMMAND [ARGS]...
```

## Global Options

- `--version` - Show RFD version
- `--help` - Show help message
- `--debug` - Enable debug output

## Commands Overview

| Command | Description | Common Usage |
|---------|-------------|--------------|
| `init` | Initialize RFD in project | `rfd init --wizard` |
| `check` | Quick status check | `rfd check` |
| `session` | Manage dev sessions | `rfd session start <feature>` |
| `build` | Build current feature | `rfd build` |
| `validate` | Validate against spec | `rfd validate` |
| `checkpoint` | Save working state | `rfd checkpoint "message"` |
| `spec` | Manage specifications | `rfd spec generate --type all` |
| `feature` | Manage features | `rfd feature add` |
| `memory` | Manage AI memory | `rfd memory show` |
| `revert` | Revert to checkpoint | `rfd revert` |

## Detailed Command Reference

### `rfd init`
Initialize RFD in your project.

```bash
# Simple initialization
rfd init

# Interactive wizard (RECOMMENDED)
rfd init --wizard

# Import from PRD document
rfd init --from-prd requirements.md

# Specify development mode
rfd init --wizard --mode 0-to-1      # Greenfield (default)
rfd init --wizard --mode brownfield  # Existing project
rfd init --wizard --mode exploration # Research project
```

**Options:**
- `--wizard` - Run interactive initialization wizard
- `--from-prd PATH` - Initialize from PRD document
- `--mode [0-to-1|brownfield|exploration]` - Development mode

**Creates:**
- `PROJECT.md` - Project specification
- `CLAUDE.md` - AI assistant configuration  
- `PROGRESS.md` - Progress tracking
- `.rfd/` - RFD system directory
- `specs/` - Specification documents (with wizard)

---

### `rfd check`
Quick health check of current project state.

```bash
rfd check
```

**Output shows:**
- Validation status (✅/❌)
- Build status (✅/❌)
- Current session info
- Active features
- Suggested next action

**Example output:**
```
=== RFD Status Check ===

📋 Validation: ✅
🔨 Build: ❌
📝 Session: user_auth (started 2024-01-15T10:30:00)

📦 Features:
  ✅ setup (12 checkpoints)
  🔨 user_auth (3 checkpoints)
  ⭕ billing (0 checkpoints)

→ Next: rfd build  # Fix build errors
```

---

### `rfd session`
Manage development sessions for features.

```bash
# Start new session
rfd session start user_auth

# End current session
rfd session end
rfd session end --failed  # Mark as failed

# List all sessions
rfd session list

# Show current session
rfd session current

# Restore from snapshot
rfd session restore <snapshot-id>
```

**Subcommands:**
- `start <feature-id>` - Start working on a feature
- `end [--success|--failed]` - End current session
- `list` - Show session history
- `current` - Show active session
- `restore <id>` - Restore from snapshot

**Session lifecycle:**
1. `start` creates context in `.rfd/context/current.md`
2. Work is tracked in `.rfd/memory.db`
3. `end` creates snapshot in `.rfd/context/snapshots/`

---

### `rfd build`
Build/compile the current feature.

```bash
# Build current feature
rfd build

# Build specific feature
rfd build user_auth

# Build with verbose output
rfd build --verbose
```

**Options:**
- `[feature-id]` - Specific feature to build (optional)
- `--verbose` - Show detailed build output

**Build process:**
1. Detects language/framework from PROJECT.md
2. Runs appropriate build commands
3. Validates build success
4. Updates build status

---

### `rfd validate`
Validate project against specifications.

```bash
# Quick validation
rfd validate

# Validate specific feature
rfd validate --feature user_auth

# Full validation (all features)
rfd validate --full

# Verbose output
rfd validate --verbose
```

**Options:**
- `--feature NAME` - Validate specific feature
- `--full` - Run complete validation
- `--verbose` - Show detailed results

**Validates:**
- File count limits
- Lines per file limits
- Test requirements
- API contracts
- Database state
- Feature acceptance criteria

**Example output:**
```
=== Validation Report ===

✅ max_files: 45 files (max: 50)
✅ max_loc_per_file: All files within limits
✅ must_pass_tests: All tests passing
✅ api_contract: All endpoints responding
❌ feature_user_auth: 3/5 acceptance criteria met

Overall: ❌ FAILING
```

---

### `rfd checkpoint`
Save a checkpoint of current working state.

```bash
# Save checkpoint with message
rfd checkpoint "Implemented login endpoint"

# Checkpoint with git commit
rfd checkpoint "Feature complete" --commit

# Checkpoint without validation
rfd checkpoint "WIP: Debugging" --skip-validation
```

**Options:**
- `message` - Description of checkpoint (required)
- `--commit` - Also create git commit
- `--skip-validation` - Skip validation (not recommended)

**Checkpoint includes:**
- Validation status
- Build status
- Git commit hash
- Timestamp
- Evidence/metadata

---

### `rfd spec`
Manage project specifications.

```bash
# Create new spec interactively
rfd spec create

# Review current specifications
rfd spec review

# Validate spec compliance
rfd spec validate

# Generate specifications
rfd spec generate              # Generate all
rfd spec generate --type all   # Generate all
rfd spec generate --type constitution
rfd spec generate --type phases
rfd spec generate --type api
rfd spec generate --type guidelines
rfd spec generate --type adr
```

**Subcommands:**
- `create` - Interactive spec creation
- `review` - Display current spec
- `validate` - Check spec validity
- `generate` - Generate spec documents

**Generated files (in `specs/`):**
- `CONSTITUTION.md` - Project principles
- `PHASES.md` - Development phases
- `API_CONTRACT.md` - API specifications
- `DEVELOPMENT_GUIDELINES.md` - Coding standards
- `ADR-001-tech-stack.md` - Architecture decisions

---

### `rfd feature`
Manage project features.

```bash
# Add new feature
rfd feature add

# List all features
rfd feature list

# Update feature status
rfd feature update user_auth --status complete

# Show feature details
rfd feature show user_auth

# Remove feature
rfd feature remove old_feature
```

**Subcommands:**
- `add` - Add new feature interactively
- `list` - Show all features
- `update <id>` - Update feature properties
- `show <id>` - Show feature details
- `remove <id>` - Remove feature

**Update options:**
- `--status [pending|building|testing|complete|blocked]`
- `--priority [critical|high|medium|low]`
- `--assigned-to NAME`

---

### `rfd memory`
Manage AI assistant memory.

```bash
# Show current memory
rfd memory show

# Reset memory
rfd memory reset

# Export memory
rfd memory export memory_backup.json

# Import memory
rfd memory import memory_backup.json

# Clear specific key
rfd memory clear current_feature
```

**Subcommands:**
- `show` - Display memory contents
- `reset` - Clear all memory
- `export <file>` - Export to file
- `import <file>` - Import from file
- `clear <key>` - Clear specific key

**Memory contains:**
- Current feature
- Last validation results
- Common errors
- Working patterns
- Session history

---

### `rfd revert`
Revert to last working checkpoint.

```bash
# Revert to last passing checkpoint
rfd revert

# Revert to specific checkpoint
rfd revert --checkpoint <id>

# Dry run (show what would change)
rfd revert --dry-run

# Force revert (ignore uncommitted changes)
rfd revert --force
```

**Options:**
- `--checkpoint ID` - Specific checkpoint ID
- `--dry-run` - Preview changes
- `--force` - Force revert

**Revert process:**
1. Finds last checkpoint where validation + build passed
2. Git reset to checkpoint commit
3. Restores session state
4. Updates context files

---

### `rfd metrics`
Display project metrics.

```bash
# Show all metrics
rfd metrics

# Show specific metric
rfd metrics --type progress
rfd metrics --type quality
rfd metrics --type velocity

# Export metrics
rfd metrics --export metrics.json

# Update metrics in PROJECT.md
rfd metrics --update
```

**Options:**
- `--type [progress|quality|velocity]` - Metric category
- `--export FILE` - Export to file
- `--update` - Update PROJECT.md

**Metrics shown:**
- Total/passing/failed checkpoints
- Feature completion rate
- Average feature time
- Drift incidents
- Test coverage
- Code quality score

---

### `rfd project`
Manage PROJECT.md file.

```bash
# Sync PROJECT.md with database
rfd project sync

# Validate PROJECT.md schema
rfd project validate

# Update specific field
rfd project update --field version --value 1.1.0

# Show project info
rfd project show
```

**Subcommands:**
- `sync` - Sync with database
- `validate` - Validate schema
- `update` - Update field
- `show` - Display project info

---

### `rfd recover`
Recover from crashes or corrupted state.

```bash
# Auto-recover to last good state
rfd recover

# Recover from specific snapshot
rfd recover --snapshot <id>

# Rebuild database from files
rfd recover --rebuild

# Check and fix integrity
rfd recover --check
```

**Options:**
- `--snapshot ID` - Recover from snapshot
- `--rebuild` - Rebuild database
- `--check` - Check integrity

**Recovery process:**
1. Checks database integrity
2. Validates file system state
3. Finds last consistent checkpoint
4. Restores to working state

---

## Environment Variables

```bash
# Enable debug output
export RFD_DEBUG=1

# Set custom RFD directory
export RFD_DIR=/path/to/.rfd

# Set session timeout (minutes)
export RFD_SESSION_TIMEOUT=120

# Enable strict mode (fail fast)
export RFD_STRICT=1

# Custom database path
export RFD_DB=/path/to/memory.db
```

---

## Configuration Files

### `.rfdrc`
Local configuration (project root):
```yaml
# Project-specific settings
auto_validate: true
strict_mode: false
checkpoint_frequency: on_commit
session_timeout: 120
```

### `~/.config/rfd/config.yaml`
Global configuration:
```yaml
# User preferences
default_mode: wizard
preferred_language: python
preferred_framework: fastapi
auto_backup: true
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Validation failed |
| 2 | Build failed |
| 3 | Feature not found |
| 4 | Session error |
| 5 | Database error |
| 10 | Configuration error |

---

## Common Workflows

### Starting Fresh
```bash
rfd init --wizard
rfd spec generate --type all
rfd session start first_feature
rfd build
rfd validate
rfd checkpoint "Initial implementation"
```

### Daily Development
```bash
rfd check                          # See where you left off
rfd session start user_auth        # Continue feature
rfd build                          # Build changes
rfd validate                       # Check compliance
rfd checkpoint "Added validation"  # Save progress
rfd session end                    # End of day
```

### Recovering from Problems
```bash
rfd check                    # Assess situation
rfd validate --full          # Find issues
rfd revert                   # Go to last good state
rfd session start user_auth  # Resume work
```

### Adding New Features
```bash
rfd feature add              # Interactive addition
rfd spec generate --type api # Generate API specs
rfd session start new_feature # Start work
```

---

## Troubleshooting

### "No feature specified"
```bash
rfd session start <feature-id>  # Start a session first
```

### "Validation failed"
```bash
rfd validate --verbose  # See detailed errors
rfd spec review        # Check requirements
```

### "Lost context"
```bash
rfd check                      # Current status
cat .rfd/context/current.md    # Session details
rfd memory show               # Memory state
```

### "Database locked"
```bash
rfd recover --check  # Fix database
```

### "Can't find PROJECT.md"
```bash
rfd init  # Initialize RFD first
```

---

## Tips & Best Practices

1. **Always use `--wizard` for init** - It generates comprehensive specs
2. **Run `rfd check` frequently** - Stay oriented
3. **Checkpoint often** - Save every small success
4. **End sessions properly** - Creates recovery snapshots
5. **Use verbose flags when debugging** - More information helps
6. **Trust validation over intuition** - Reality beats assumptions
7. **Keep features small** - Easier to complete and validate
8. **Update PROJECT.md regularly** - Keep spec current
9. **Review metrics weekly** - Track progress trends
10. **Use recovery early** - Don't wait until totally stuck