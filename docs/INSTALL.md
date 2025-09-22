# RFD Protocol Installation Guide

This guide covers installing and setting up the Nexus RFD Protocol in new projects.

## Prerequisites

- **Python 3.8+** (required)
- **Git** (recommended for checkpoints)
- **Claude Code CLI** (optional but recommended)

## Installation Methods

### Method 1: pip install (Recommended)

```bash
pip install nexus-rfd-protocol
```

Verify installation:
```bash
rfd --version
```

### Method 2: pipx install (Isolated)

For global CLI access without affecting your Python environment:

```bash
pipx install nexus-rfd-protocol
```

### Method 3: Development Install

For contributing or local development:

```bash
git clone https://github.com/nexus-dev/rfd-protocol.git
cd rfd-protocol
pip install -e .
```

## Project Setup

### Step 1: Initialize RFD

Navigate to your project directory and initialize:

```bash
cd your-project/
rfd init
```

This creates:
- `PROJECT.md` - Project specification
- `CLAUDE.md` - Claude Code configuration  
- `PROGRESS.md` - Build progress log
- `.rfd/` - RFD system directory

### Step 2: Configure Your Specification

The init command runs an interactive wizard, or you can edit `PROJECT.md` manually:

```markdown
---
version: "1.0"
name: "My Project"
stack:
  language: python          # python, javascript, typescript, go, rust, etc.
  framework: fastapi        # fastapi, express, django, react, etc.
  database: sqlite          # sqlite, postgresql, mysql, mongodb, none
features:
  - id: core_feature
    description: "Core functionality"
    acceptance: "Feature works as specified"
    status: pending
rules:
  max_files: 20
  max_loc_per_file: 200
  must_pass_tests: true
---

# My Project Description

What your project does...
```

### Step 3: Verify Setup

```bash
rfd check
```

Should show:
```
=== RFD Status Check ===

📋 Validation: ❌ (no features built yet)
🔨 Build: ❌ (no code yet)

📦 Features:
  ⭕ core_feature (0 checkpoints)

→ Next: rfd session start core_feature
```

## Integration with Claude Code

### Automatic Integration

If you have Claude Code CLI installed, RFD automatically configures it:

1. **CLAUDE.md** is created with RFD-specific instructions
2. **Memory persistence** is configured at `.rfd/context/memory.json`
3. **Claude follows RFD workflow** automatically

### Manual Claude Code Setup

If using Claude through other interfaces, follow this workflow:

1. **Read specification**: `@PROJECT.md`
2. **Check current task**: `@.rfd/context/current.md`  
3. **Follow commands**: `rfd build && rfd validate`
4. **Save progress**: `rfd checkpoint "message"`

## Technology Stack Configuration

### Python Projects

RFD auto-detects:
- **FastAPI**: Uvicorn server, health checks
- **Flask**: Development server
- **Django**: Management commands

Dependencies in `requirements.txt` are auto-installed during build.

### JavaScript/TypeScript Projects

RFD auto-detects:
- **Express**: Node.js server
- **React**: Create React App or Vite
- **Next.js**: Next.js development server

Dependencies in `package.json` are auto-installed.

### Go Projects

RFD auto-detects:
- **Gin/Echo**: HTTP servers
- **Standard library**: Basic HTTP

Uses `go.mod` for dependency management.

### Other Languages

RFD supports any language through custom build commands in PROJECT.md:

```yaml
stack:
  language: rust
  framework: actix-web
  build_commands:
    - "cargo build"
    - "cargo test"
    - "cargo run --bin server"
```

## Directory Structure After Install

```
your-project/
├── PROJECT.md              # ← Project specification (edit this)
├── CLAUDE.md               # ← Claude Code integration
├── PROGRESS.md             # ← Build history (auto-updated)
├── .rfd/                   # ← RFD system files
│   ├── memory.db           #   SQLite database for state
│   └── context/            #   AI context and memory
│       ├── current.md      #   Current session info
│       ├── memory.json     #   AI memory persistence
│       └── checkpoints/    #   Checkpoint storage
├── requirements.txt        # ← Your dependencies (if Python)
├── package.json           # ← Your dependencies (if JS/TS)
└── [your source code]     # ← Your actual project files
```

## Common Setup Patterns

### API Project Setup

```bash
mkdir my-api && cd my-api
rfd init
# Choose: Python + FastAPI + SQLite
echo "fastapi[all]==0.104.1" > requirements.txt
rfd session start user_auth
```

### Frontend Project Setup  

```bash
mkdir my-app && cd my-app
rfd init  
# Choose: TypeScript + React + None
npm create vite@latest . -- --template react-ts
rfd session start user_interface
```

### Full Stack Setup

```bash
mkdir my-fullstack && cd my-fullstack
rfd init
# Choose: Python + FastAPI + PostgreSQL

# Add multiple features
rfd spec review  # Edit PROJECT.md to add frontend feature
```

## Verification Checklist

After installation, verify everything works:

- [ ] `rfd --version` shows version number
- [ ] `rfd init` creates PROJECT.md, CLAUDE.md, PROGRESS.md
- [ ] `rfd check` shows status (even if failing)
- [ ] `rfd spec review` displays your specification
- [ ] `.rfd/` directory exists with proper structure

## Troubleshooting Installation

### Command not found: rfd

**Problem**: `rfd` command not available after pip install

**Solutions**:
```bash
# Option 1: Add to PATH
export PATH="$PATH:$HOME/.local/bin"

# Option 2: Use python -m
python -m nexus_rfd_protocol.cli --help

# Option 3: Use pipx instead  
pipx install nexus-rfd-protocol
```

### Permission errors

**Problem**: Cannot create .rfd directory

**Solution**:
```bash
# Ensure write permissions
chmod 755 .
# Or run in different directory
mkdir temp-project && cd temp-project && rfd init
```

### Import errors

**Problem**: Module not found errors

**Solution**:
```bash
# Reinstall with dependencies
pip install --upgrade --force-reinstall nexus-rfd-protocol

# Or install with all optional dependencies
pip install nexus-rfd-protocol[dev]
```

### Claude Code not auto-configured

**Problem**: CLAUDE.md created but Claude Code doesn't follow RFD workflow

**Solution**:
```bash
# Verify CLAUDE.md exists and has correct content
cat CLAUDE.md

# Restart Claude Code CLI
# Ensure CLAUDE.md is in project root
```

## Next Steps

After successful installation:

1. **Create your first feature**: `rfd session start first_feature`
2. **Follow RFD workflow**: Build → Validate → Checkpoint
3. **Read the main README.md** for detailed usage
4. **Check examples** in the repository

## Uninstallation

To remove RFD from a project:

```bash
# Remove RFD files (optional - keeps your code)
rm -rf .rfd/ PROJECT.md CLAUDE.md PROGRESS.md

# Uninstall package
pip uninstall nexus-rfd-protocol
```

Your source code remains untouched.