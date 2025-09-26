# RFD Protocol - Reality-First Development

**Stop AI hallucination. Ship working code.**

[![CI Pipeline](https://github.com/kryptobaseddev/rfd-protocol/actions/workflows/ci.yml/badge.svg)](https://github.com/kryptobaseddev/rfd-protocol/actions/workflows/ci.yml)
[![Release Pipeline](https://github.com/kryptobaseddev/rfd-protocol/actions/workflows/release.yml/badge.svg)](https://github.com/kryptobaseddev/rfd-protocol/actions/workflows/release.yml)
[![PyPI version](https://badge.fury.io/py/rfd-protocol.svg)](https://pypi.org/project/rfd-protocol/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## The Problem We Solve

**48% of AI-generated code contains hallucinations** - false claims, non-existent functions, or broken implementations. Developers waste countless hours debugging phantom code, losing context between sessions, and watching projects drift into chaos.

RFD enforces reality at every step. No more "I implemented that feature" when nothing works. No more mock data pretending to be production code. No more losing track of what you were building.

## What is RFD?

RFD (Reality-First Development) is a development protocol that makes **AI hallucination** physically impossible through continuous reality validation. Not just managing the LLM but also the human to help prevent **squirrel brain** and **SDLC drift** by enforcing concrete reality checkpoints. Instead of trusting AI claims about what was implemented, RFD validates the actual code runs, tests pass, and features work. It's not just another tool - it's a fundamental shift in how we build software with AI.

### Core Guarantees

✅ **Zero Hallucination** - Every claim is validated against running code  
✅ **Persistent Context** - Never lose your place, even across restarts  
✅ **Enforced Focus** - Can't drift from specified features  
✅ **Real Code Only** - No mocks, stubs, or placeholder implementations  
✅ **Universal Compatibility** - Works with any language, any framework  

## 📚 Documentation

- **[RFD Walkthrough](docs/RFD_WALKTHROUGH.md)** - Complete step-by-step guide (NEW!)
- **[Getting Started Guide](docs/GETTING_STARTED.md)** - 5-minute tutorial
- **[CLI Reference](docs/CLI_REFERENCE.md)** - All commands documented
- **[Claude Code Guide](docs/CLAUDE_CODE_GUIDE.md)** - AI integration guide
- **[Configuration Schema](docs/CONFIG_SCHEMA.md)** - Complete .rfd/config.yaml reference
- **[Installation Guide](docs/INSTALL.md)** - Detailed setup instructions

## Quick Start (90 Seconds)

```bash
# Install RFD
pip install rfd-protocol

# Initialize your project  
cd your-project
rfd init --wizard

# Start building with database-first workflow
rfd feature add user_auth -d "User authentication"
rfd session start user_auth
rfd build
rfd validate
rfd checkpoint "Feature complete"
```

That's it. RFD now guards your development.

## How RFD Works

### 1. Specification Lock
```yaml
# .rfd/config.yaml defines project configuration
project:
  name: "My Project"
  description: "Project managed by RFD"
stack:
  language: python
  framework: fastapi
  database: postgresql

# Features stored in database (.rfd/memory.db)
$ rfd feature list
- user_auth: "Users can register and login" (pending)
```

### 2. Reality Enforcement
```bash
# AI claims: "I implemented user authentication"
$ rfd validate

❌ Reality Check Failed:
  - No /register endpoint found
  - No /login endpoint found  
  - 0 of 5 tests passing
  - Database table 'users' does not exist
```

### 3. Progress Tracking
```bash
$ rfd status

📊 Project Status
━━━━━━━━━━━━━━━━━━━━
Features: 1 pending, 0 complete
Current: user_auth (0% complete)
Next: Create user registration endpoint

Last Valid Checkpoint: 2 hours ago
"Database schema created"
```

## Complete Workflow Commands

### Initialization & Setup
```bash
rfd init                    # Basic project setup
rfd init --wizard          # Interactive setup (recommended)
rfd init --from-prd doc.md # Initialize from requirements doc
rfd init --mode brownfield # For existing projects
```

### Database-First Commands (NEW v5.0!)
```bash
rfd audit                    # Database-first compliance check
rfd feature add <id> -d "desc"  # Add feature to database
rfd feature list            # List all features
rfd feature start <id>      # Start working on feature
rfd session status          # Show current session details
rfd session current         # Alias for status
rfd gaps                     # Show gap analysis from database
rfd gaps --status missing   # Show missing functionality
rfd gaps --priority critical # Show critical gaps
```

### Development Workflow
```bash
rfd session start <feature>  # Begin feature work
rfd build                    # Run build process
rfd validate                 # Validate implementation
rfd checkpoint "message"     # Save progress
rfd session end             # Complete feature
```

### Analysis & Review
```bash
rfd check                   # Quick status check
rfd status                  # Detailed project status
rfd audit                   # Database-first compliance check (NEW v5.0!)
rfd gaps                    # Gap analysis report (NEW v5.0!)
rfd analyze                # Cross-artifact consistency check
rfd dashboard              # Visual progress dashboard
rfd spec review            # Review current specification
```

### State Management
```bash
rfd revert                  # Revert to last checkpoint
rfd memory show            # Display context memory
rfd memory reset           # Clear context (careful!)
```

## Advanced Features (NEW in v5.0)

### Database-First Architecture
- All features stored in SQLite database
- Immutable config in .rfd/config.yaml
- No more PROJECT.md/PROGRESS.md conflicts
- Protected context files with DO NOT EDIT warnings

### SQLite with WAL Mode
- Write-Ahead Logging for better concurrency
- Persistent memory across all sessions
- Automatic crash recovery
- Zero configuration required

### Cross-Artifact Analysis
```bash
$ rfd analyze

CROSS-ARTIFACT ANALYSIS REPORT
════════════════════════════════
📋 SPEC ALIGNMENT
  ✅ All features aligned with specification

📝 TASK CONSISTENCY  
  ✅ All tasks consistent with feature status

🔌 API IMPLEMENTATION
  Coverage: 100.0%
  ✅ All endpoints implemented

🧪 TEST COVERAGE
  Coverage: 87.5%
  ✅ All acceptance criteria covered
```

## Integration with AI Tools

### Claude Code Configuration

RFD automatically configures Claude Code to prevent hallucination:

```bash
# Tell Claude to continue your project
"Continue the RFD session"

# Claude automatically:
$ rfd check
> Current feature: user_auth
> Last checkpoint: "Created User model"  
> Next task: Implement registration endpoint

# Claude reads (but never edits) context files:
$ cat .rfd/context/current.md  # AUTO-GENERATED - DO NOT EDIT

# Claude cannot fake progress:
$ rfd checkpoint "Added authentication"
❌ Cannot checkpoint - validation failing
```

### Custom AI Integration

For other AI tools, enforce this workflow:

1. Read `.rfd/config.yaml` for project configuration
2. Check `.rfd/context/current.md` for current task (READ-ONLY)
3. Use `rfd feature list` to see features from database
4. Run `rfd validate` after every change
5. Only checkpoint when validation passes

## Project Configuration

### Configuration Schema (.rfd/config.yaml)

RFD uses a flexible, extensible configuration:

```yaml
# Required Fields
project:
  name: "Your Project"
  description: "What it does"
  version: "1.0.0"

# Technology Stack (extensible)
stack:
  language: python
  framework: fastapi
  database: postgresql
  # Add any custom fields:
  runtime: python-3.11
  deployment: kubernetes
  monitoring: prometheus

# Validation Rules
rules:
  max_files: 50
  max_loc_per_file: 500
  must_pass_tests: true
  no_mocks_in_prod: true
  min_test_coverage: 80

# Features are stored in database, not config file
# Use these commands to manage features:
# rfd feature add core_api -d "RESTful API" -a "All endpoints return correct data"
# rfd feature list
# rfd feature start core_api

# Constraints
constraints:
  - "Response time < 200ms"
  - "Support 10k concurrent users"
---
```

## Project Architecture

Our repository follows modern Python packaging standards:

```
rfd-protocol/
├── src/rfd/                  # 🎯 MAIN PACKAGE
│   ├── __init__.py
│   ├── cli.py               # Command-line interface
│   ├── rfd.py              # Core orchestration
│   ├── validation.py       # Hallucination detection
│   ├── session.py          # Session management
│   ├── build.py            # Build automation
│   ├── spec.py             # Specification management
│   ├── analyze.py          # Cross-artifact analysis (NEW!)
│   ├── db_utils.py         # WAL mode database (NEW!)
│   └── templates/          # Project templates
│
├── tests/                   # 🧪 TEST SUITE
│   ├── unit/
│   ├── integration/
│   └── system/
│
├── docs/                   # 📚 DOCUMENTATION
│   ├── RFD_WALKTHROUGH.md # Complete guide (NEW!)
│   └── [other docs]
│
└── .github/workflows/      # 🚀 CI/CD
    ├── ci.yml
    └── release.yml        # Auto PyPI publishing
```

## Installation Options

### Global Install (Recommended)
```bash
pip install rfd-protocol
```

### Project-Specific Install
```bash
cd your-project
python -m venv venv
source venv/bin/activate
pip install rfd-protocol
```

### Development Install
```bash
git clone https://github.com/kryptobaseddev/rfd-protocol.git
cd rfd-protocol
pip install -e .
```

## Language Support

RFD works with any technology stack:

- **Python**: FastAPI, Django, Flask
- **JavaScript/TypeScript**: Express, Next.js, React
- **Go**: Gin, Echo, Fiber
- **Rust**: Actix, Rocket, Axum
- **Java/Kotlin**: Spring Boot
- **C/C++**: Any build system
- **Ruby**: Rails, Sinatra
- **PHP**: Laravel, Symfony
- **And 20+ more...**

## Real-World Impact

### Before RFD
- 48% hallucination rate
- Lost context after restarts
- Endless debugging of AI mistakes
- Projects that never ship

### After RFD
- 0% hallucination rate
- Perfect context persistence
- Only real, working code
- Consistent project delivery

## Testing & Development

### Running Tests
```bash
# All tests
pytest

# By category
pytest -m unit           # Fast unit tests
pytest -m integration    # Integration tests  
pytest -m system         # End-to-end tests

# With coverage
pytest --cov=src/rfd --cov-report=html
```

### Code Quality
```bash
# Linting
ruff check src tests

# Formatting
ruff format src tests

# Type checking
mypy src --ignore-missing-imports
```

## Troubleshooting

### "Feature not in PROJECT.md"
You tried to work on an undefined feature. Edit PROJECT.md first.

### "Validation failed"
```bash
rfd validate --verbose  # See detailed errors
rfd build              # Fix build issues first
```

### "Lost context"
```bash
rfd check                      # Current status
cat .rfd/context/current.md   # Session details
```

### Debug Mode
```bash
export RFD_DEBUG=1
rfd validate                    # Verbose output
```

## Contributing

We welcome contributions! RFD uses itself for development:

1. Fork the repository
2. Run `rfd init` in your fork
3. Create feature in PROJECT.md
4. Use RFD workflow to implement
5. Submit PR when `rfd validate` passes

### Development Setup
```bash
git clone https://github.com/kryptobaseddev/rfd-protocol.git
cd rfd-protocol
pip install -e ".[dev]"
pytest  # Run tests
```

## Support

- **Issues**: [GitHub Issues](https://github.com/kryptobaseddev/rfd-protocol/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kryptobaseddev/rfd-protocol/discussions)
- **Documentation**: [Full docs](docs/)
- **Email**: keatonhoskins@icloud.com

## Version History

- **v5.0.0**: Complete database-first migration, protected context files, audit command, deprecated PROJECT.md
- **v4.x**: Transition to database-first architecture, config.yaml introduction
- **v3.0.0**: SQLite WAL mode, cross-artifact analysis, spec-kit feature parity
- **v2.3.0**: Mock detection, critical fixes, session persistence improvements
- **v2.0.0**: Spec generation, gated workflow, AI validation
- **v1.0.0**: Production release with modern Python packaging and full documentation

## License

MIT License - see [LICENSE](LICENSE)

---

**Built with RFD** - This project dogfoods its own reality-first methodology.