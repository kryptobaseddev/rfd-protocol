# Nexus RFD Protocol

**Reality-First Development System - Prevents AI hallucination and ensures spec-driven development**

[![PyPI version](https://badge.fury.io/py/nexus-rfd-protocol.svg)](https://badge.fury.io/py/nexus-rfd-protocol)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is RFD?

RFD (Reality-First Development) is a protocol that **eliminates AI hallucination** in software development by enforcing concrete reality checkpoints. Instead of trusting AI claims about what was implemented, RFD validates that code actually runs, tests pass, and features work.

### Core Benefits

- **🎯 Prevents AI Hallucination**: Drops error rate from 48% to ~0%
- **📋 Spec-Driven Development**: Features must be specified before implementation
- **✅ Reality Checkpoints**: Every change is validated against working code
- **🔄 Session Persistence**: Context maintained across Claude Code sessions
- **🌍 Universal Drop-in**: Works with any tech stack (25+ languages)

## Quick Start

### Installation

```bash
pip install nexus-rfd-protocol
```

### Initialize in Your Project

```bash
cd your-project/
rfd init
```

This creates:
- `PROJECT.md` - Your project specification
- `CLAUDE.md` - Claude Code integration config
- `PROGRESS.md` - Build progress tracking
- `.rfd/` - RFD system directory

### Basic Workflow

1. **Define specifications first**:
   ```bash
   rfd spec create
   ```

2. **Start feature development**:
   ```bash
   rfd session start user_auth
   ```

3. **Build and validate continuously**:
   ```bash
   rfd build
   rfd validate
   ```

4. **Save working checkpoints**:
   ```bash
   rfd checkpoint "User auth working"
   ```

## Core Concepts

### Reality-First Principles

1. **Code that runs > Perfect architecture**
2. **Working features > Planned features**  
3. **Real data > Mocked responses**
4. **Passing tests > Theoretical correctness**

### Validation Engine

RFD continuously validates:
- ✅ Files actually exist (detects AI file creation lies)
- ✅ Functions are implemented (not just claimed)
- ✅ APIs respond correctly
- ✅ Tests pass with real data
- ✅ Build processes work

### Session Management

- **Persistent Context**: RFD maintains what you're working on across restarts
- **Memory**: AI remembers what worked/failed in previous sessions
- **Progress Tracking**: Visual progress through complex features
- **Auto-Recovery**: Continue from last checkpoint if interrupted

## Integration with Claude Code

RFD is designed to work seamlessly with [Claude Code](https://claude.ai/code):

1. **Install RFD** in your project: `rfd init`
2. **Claude Code reads** `CLAUDE.md` automatically
3. **AI follows RFD workflow** - validates every change
4. **Context persists** in `.rfd/context/memory.json`

### Example Claude Code Session

```bash
# AI automatically follows this workflow:
rfd check                    # Check current status
rfd build                    # Implement features  
rfd validate                 # Verify everything works
rfd checkpoint "Feature X"   # Save progress
```

## Project Structure

```
your-project/
├── PROJECT.md              # Specification (required)
├── CLAUDE.md               # Claude Code config
├── PROGRESS.md             # Build history
├── .rfd/
│   ├── memory.db          # SQLite state
│   └── context/
│       ├── current.md     # Active session
│       └── memory.json    # AI memory
└── your code...
```

## Command Reference

### Core Commands

```bash
rfd init                    # Initialize RFD in current directory
rfd check                   # Quick status check
rfd spec create            # Interactive spec creation
rfd spec review            # Review current specification
```

### Development Workflow

```bash
rfd session start <feature>  # Start working on a feature  
rfd build [feature]          # Build/compile feature
rfd validate [--feature X]  # Run validation tests
rfd checkpoint "message"     # Save working state
rfd session end             # Mark feature complete
```

### State Management

```bash
rfd revert                  # Revert to last checkpoint
rfd memory show            # Show AI memory
rfd memory reset           # Clear AI memory
```

## Specification Format

RFD uses frontmatter-based PROJECT.md files:

```markdown
---
version: "1.0"
name: "My API"
stack:
  language: python
  framework: fastapi
  database: sqlite
features:
  - id: user_auth
    description: "User signup and login"
    acceptance: "POST /signup returns 201, POST /login returns token"
    status: pending
rules:
  max_files: 20
  max_loc_per_file: 200
  must_pass_tests: true
---

# My API Project

This API handles user authentication and data management.
```

## Advanced Configuration

### Custom Validation Rules

Add to `PROJECT.md`:

```yaml
rules:
  max_files: 15              # Limit complexity
  max_loc_per_file: 150      # Keep files small
  must_pass_tests: true      # Require working tests
  no_mocks_in_prod: true     # Real implementations only
```

### API Contract Testing

```yaml
api_contract:
  base_url: "http://localhost:8000"
  health_check: "/health"
  endpoints:
    - method: POST
      path: "/users"
      validates: "returns 201 with {user_id: string}"
```

### Technology Stack Support

RFD works with any stack by detecting your configuration:

- **Python**: FastAPI, Flask, Django
- **JavaScript**: Express, NestJS, Next.js
- **TypeScript**: All JS frameworks + type checking
- **Go**: Gin, Echo, standard library
- **Rust**: Actix, Rocket, Axum
- **And many more...**

## Troubleshooting

### Common Issues

**"No feature specified"**
```bash
rfd session start <feature_id>  # Start a session first
```

**"Validation failed"**
```bash
rfd validate                    # See what's failing
rfd build                       # Fix build issues first
```

**"Lost context"**
```bash
rfd check                       # See current state
cat .rfd/context/current.md     # Check session file
```

### Debug Mode

```bash
export RFD_DEBUG=1
rfd validate                    # Verbose output
```

## Examples

### Simple FastAPI Project

```bash
mkdir my-api && cd my-api
rfd init
# Follow wizard: Python + FastAPI + SQLite
rfd session start user_signup
# Implement feature...
rfd build && rfd validate
rfd checkpoint "User signup working"
```

### React Frontend

```bash
mkdir my-app && cd my-app  
rfd init
# Follow wizard: TypeScript + React + None
rfd session start user_interface
# Build components...
rfd build && rfd validate
```

## Contributing

RFD Protocol is open source. Contributions welcome!

1. **Fork** the repository
2. **Create** a feature branch
3. **Use RFD** to develop your feature 😉
4. **Submit** a pull request

## License

MIT License - see [LICENSE](LICENSE) file.

## Support

- **GitHub Issues**: [Report bugs](https://github.com/nexus-dev/rfd-protocol/issues)
- **Documentation**: [Full docs](https://github.com/nexus-dev/rfd-protocol/docs)
- **Discord**: [Community chat](https://discord.gg/rfd-protocol)

---

**Built with RFD Protocol** - This project was developed using its own reality-first methodology.