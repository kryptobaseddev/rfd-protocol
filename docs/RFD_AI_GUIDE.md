# RFD v5.0.0 - AI Agent Guide

## Installation
```bash
pip install --upgrade rfd-protocol
rfd --version  # Should show 5.0.0
```

## Core Commands for AI Agents

### 🚀 Getting Started
```bash
rfd init                    # Initialize RFD in a project
rfd check                   # Quick health check
rfd status                  # Comprehensive project status
```

### 📦 Feature Management (Database-First)
```bash
rfd feature list            # List all features from database
rfd feature add <id> -d "description"  # Add new feature
rfd feature start <id>      # Start working on a feature
rfd feature complete <id>   # Mark feature as complete
rfd feature show <id>       # Show feature details
```

### 📝 Session Management
```bash
rfd session start <feature> # Start development session
rfd session status          # Show current session (NEW in v5!)
rfd session current         # Alias for status (NEW in v5!)
rfd session end             # End current session
```

### ✅ Validation & Testing
```bash
rfd build                   # Build current feature
rfd validate                # Run validation tests
rfd validate --feature <id> # Validate specific feature
rfd audit                   # Database-first compliance (NEW in v5!)
```

### 💾 Progress Tracking
```bash
rfd checkpoint "message"    # Save progress checkpoint
rfd dashboard              # Visual progress overview
rfd resume                 # Resume from last context
```

### 📋 Specifications
```bash
rfd spec                   # Show project configuration
rfd spec review            # Review specifications
rfd spec validate          # Validate spec completeness
```

### 🔍 Gap Analysis (NEW v5.0!)
```bash
rfd gaps                    # Show all gap analysis
rfd gaps --status missing  # Show missing functionality
rfd gaps --priority critical # Show critical gaps
rfd gaps --category core_problems # Show core problem gaps
rfd gaps --format json     # JSON output for tooling
```

### 🔧 Advanced Commands
```bash
rfd plan create <feature>  # Create implementation plan
rfd plan tasks <feature>   # Generate task breakdown
rfd analyze                # Cross-artifact analysis
rfd workflow start <id>    # Start gated workflow
```

## ⚠️ CRITICAL for AI Agents

### Files You Can READ but NEVER EDIT:
- `.rfd/context/current.md` - AUTO-GENERATED session context
- `.rfd/context/memory.json` - AUTO-GENERATED memory
- `.rfd/context/handoff.md` - AUTO-GENERATED handoff

### Source of Truth:
- **Configuration**: `.rfd/config.yaml`
- **Features**: Database (`.rfd/memory.db`)
- **Progress**: Checkpoints in database
- **Database**: `.rfd/memory.db` for features and progress

### Workflow for AI:
1. `rfd check` - Check project state
2. `rfd feature list` - See available features
3. `rfd session start <feature>` - Begin work
4. Read `.rfd/context/current.md` for context (DO NOT EDIT)
5. Make code changes
6. `rfd build && rfd validate` - Test changes
7. `rfd checkpoint "message"` - Save progress
8. `rfd session end` - End session

## Command Help
Every command supports `--help`:
```bash
rfd --help              # Main help
rfd session --help      # Session commands
rfd feature --help      # Feature commands
rfd spec --help         # Spec commands
```

## New v5.0.0 Features
- ✅ `rfd audit` - Checks database-first compliance
- ✅ `rfd session status/current` - Show current session
- ✅ `rfd gaps` - Database-stored gap analysis with filtering
- ✅ Protected context files with DO NOT EDIT warnings
- ✅ Complete database-first architecture
- ✅ Clean database-first architecture

## Example AI Session
```bash
# Start
rfd check
rfd feature list

# Work on feature
rfd session start authentication
# Read (don't edit) .rfd/context/current.md
# Make code changes...
rfd build
rfd validate

# Save progress
rfd checkpoint "Implemented login endpoint"
rfd session end

# Resume later
rfd resume
rfd session status
```

## Database-First Rules
1. Features ONLY exist in database
2. Use `rfd feature` commands, not manual edits
3. Context files are READ-ONLY
4. Use `rfd audit` to check compliance
5. All status from database, not files