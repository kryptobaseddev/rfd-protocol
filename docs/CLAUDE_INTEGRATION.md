# RFD Protocol - Claude Code Integration Guide

## 🚀 Quick Start

The RFD Protocol is now fully integrated with Claude Code through custom slash commands.

### Available Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/rfd-setup` | Setup environment and dependencies | Use once to initialize |
| `/rfd-init` | Initialize RFD project | Creates project structure |
| `/rfd-check` | Check project status | Shows current state |
| `/rfd-build` | Build a feature | `/rfd-build feature-id` |
| `/rfd-validate` | Validate specifications | `/rfd-validate [feature]` |
| `/rfd-fix` | Auto-fix common issues | Fixes linting, deps, etc. |
| `/rfd-session` | Manage work sessions | `/rfd-session start feature` |
| `/rfd` | Complete workflow | Builds, tests, validates |
| `/rfd-help` | Show all commands | Lists available commands |

## 💪 Bulletproof Features

### 1. Automatic Environment Setup
- Virtual environment creation
- Dependency installation
- Permission fixing
- Structure initialization

### 2. Robust Error Handling
- Graceful fallbacks for missing modules
- Helpful error messages
- Auto-recovery from common issues

### 3. Comprehensive State Management
- SQLite database for persistence
- Session tracking
- Checkpoint system
- Progress documentation

### 4. Claude Code Integration
- Native slash commands
- Proper tool permissions
- TodoWrite integration
- Contextual suggestions

## 🎯 Typical Workflow

```bash
# 1. Setup (once per project)
/rfd-setup

# 2. Initialize project
/rfd-init

# 3. Check status
/rfd-check

# 4. Work on a feature
/rfd-session start feature-1
/rfd-build feature-1
/rfd-validate feature-1

# 5. Save progress
/rfd checkpoint "Completed feature-1"

# Or use the all-in-one command:
/rfd feature-1
```

## 🛠️ Architecture

### Core Components

1. **setup.py** - Bulletproof environment setup
2. **rfd-bulletproof.py** - Production-ready RFD implementation
3. **.claude/commands/** - Claude Code slash commands
4. **.rfd/** - Project state and modules

### Key Features

- **No Manual Setup Required**: Everything auto-configures
- **Fallback Mechanisms**: Works even with partial failures
- **Progressive Enhancement**: Basic features work immediately
- **Full Integration**: Native Claude Code experience

## 🔧 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `/rfd-setup` |
| "No virtual environment" | Run `/rfd-setup` |
| Linting errors | Run `/rfd-fix` |
| Build failures | Check `/rfd-check` for status |
| Test failures | Use `/rfd-validate` to identify issues |

### Manual Recovery

If automated fixes don't work:

```bash
# Complete reset
rm -rf .venv .rfd
python3 setup.py
./rfd init
```

## 📊 Status Indicators

- ✅ **Complete**: Feature fully implemented and tested
- 🔨 **Building**: Feature in progress
- ⭕ **Pending**: Feature not started
- ❌ **Failed**: Build or validation failed

## 🎓 Best Practices

1. **Always check status first**: `/rfd-check`
2. **Use sessions for context**: `/rfd-session start feature`
3. **Validate frequently**: `/rfd-validate`
4. **Checkpoint successes**: `/rfd checkpoint "message"`
5. **Fix issues immediately**: `/rfd-fix`

## 📝 Configuration

### Configuration Structure (v5.0)

**.rfd/config.yaml:**
```yaml
project:
  name: "Your Project"
  description: "Project description"
  version: "1.0.0"
stack:
  language: "python"
  framework: "fastapi"
  database: "sqlite"
rules:
  max_files: 50
  max_loc_per_file: 1200
  must_pass_tests: true
```

**Features in Database:**
```bash
# Features are stored in .rfd/memory.db, not files
rfd feature add feature-1 -d "Feature description" -a "Test criteria"
rfd feature list  # Shows all features from database
```

### Custom Commands

Add your own commands in `.claude/commands/`:

```markdown
---
description: Your command description
allowed-tools: Bash(*), Read(*), Write(*)
---

# Command content
```

## 🎉 Success Metrics

The RFD Protocol is considered "bulletproof" when:

- ✅ All commands work without manual intervention
- ✅ Environment auto-configures correctly
- ✅ Errors are handled gracefully
- ✅ State persists across sessions
- ✅ Claude integration is seamless

## 📚 Additional Resources

- Run `/rfd-help` for command reference
- Use `rfd dashboard` for progress visualization
- Read `.rfd/context/current.md` for session state (READ-ONLY - AUTO-GENERATED)
- View `.rfd/memory.db` for persistent storage

---

*The RFD Protocol is now production-ready and fully integrated with Claude Code!*