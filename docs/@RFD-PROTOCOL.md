# Reality-First Development Protocol

## Overview
RFD (Reality-First Development) is a methodology and toolset that prevents AI hallucination and SDLC drift by validating actual progress against reality checkpoints.

## Core Principles
1. **Reality Over Theory**: Working code > Perfect documentation
2. **Validation-Driven**: Every claim must be verifiable
3. **Session Continuity**: Context persists across AI interactions
4. **Zero Tolerance for Drift**: Automatic detection and correction

## Architecture

### Components
- **Validation Engine**: Verifies AI claims and code existence
- **Session Manager**: Maintains context across sessions
- **Build Engine**: Manages feature construction
- **Spec Engine**: Handles specifications and requirements
- **Memory System**: SQLite-based state persistence

### File Structure
```
project/
├── .rfd/                  # RFD system (drop-in)
│   ├── rfd.py            # Main CLI entry point
│   ├── validation.py     # Reality validation
│   ├── session.py        # Session management
│   ├── build.py          # Build orchestration
│   ├── spec.py           # Specification handling
│   └── memory.db         # Persistent state
├── CLAUDE.md             # AI agent instructions
├── AGENTS.md             # Agent definitions
└── @RFD-PROTOCOL.md      # This file
```

## Installation
Simply copy the `.rfd` directory into any project root. No external dependencies required beyond Python 3.8+.

## Usage

### Basic Commands
```bash
# Initialize RFD in project
python .rfd/rfd.py init

# Validate current state
python .rfd/rfd.py validate

# Quick status check
python .rfd/rfd.py check

# Start feature session
python .rfd/rfd.py session start <feature-id>

# Save checkpoint
python .rfd/rfd.py checkpoint "Description"

# Revert to last working state
python .rfd/rfd.py revert
```

### AI Hallucination Prevention
RFD automatically detects when AI makes false claims about:
- Files that don't exist
- Functions/classes that weren't created
- Features that aren't implemented
- Tests that don't pass

### Universal Language Support
RFD works with any programming language:
- TypeScript/JavaScript
- Python
- Rust
- Go
- Java/Kotlin
- C/C++
- Any other language

## Reality Checkpoints

### Level 1: Specification
- Concrete acceptance criteria defined
- Test cases specified
- Dependencies identified

### Level 2: Code Execution
- No syntax errors
- No runtime errors
- Basic functionality verified

### Level 3: Test Validation
- Unit tests passing
- Integration tests passing
- Acceptance tests passing

### Level 4: Data Flow
- Real data processed successfully
- Expected outputs produced
- Performance within bounds

### Level 5: Integration
- Components interact correctly
- External dependencies resolved
- System coherence maintained

### Level 6: Acceptance
- Specification requirements met
- User acceptance achieved
- Production ready

## Session Memory

### Persistent Context
- Current feature being developed
- Validation history
- Common error patterns
- Successful implementation patterns

### Cross-Session Continuity
New AI sessions automatically:
1. Load previous context
2. Resume from last checkpoint
3. Maintain feature progress
4. Remember validation results

## Drift Prevention

### Detection Mechanisms
- Specification deviation monitoring
- Progress velocity tracking
- Checkpoint failure patterns
- Session discontinuity alerts

### Automatic Corrections
- Rollback to last working state
- Specification realignment
- Progress recalibration
- Memory state restoration

## Production Readiness

### Solo Developer Features
- Zero configuration required
- No external services needed
- Git integration included
- Automatic documentation generation

### Quality Guarantees
- No code without tests
- No features without validation
- No progress without proof
- No drift without detection

## Integration

### Claude Code CLI
RFD integrates seamlessly with Claude Code:
1. Reads CLAUDE.md for instructions
2. Validates all AI actions
3. Maintains session memory
4. Prevents hallucination

### Version Control
Works with any VCS:
- Git checkpoint integration
- Automatic commit validation
- Rollback capabilities
- Progress tracking

## Success Metrics
- Hallucination incidents: 0%
- Drift detection rate: >95%
- Session continuity: >99%
- Feature completion accuracy: >90%

## License
MIT - Free for all developers

## Support
Report issues: https://github.com/anthropics/rfd-protocol/issues