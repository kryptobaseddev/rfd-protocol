# RFD Terminology Guide

## Core Concepts

### Checkpoint
A **checkpoint** is a verified save point in your development process where:
- Code compiles/runs without errors
- Tests are passing (if required)
- Validation rules are met
- A git commit exists

**Location**: Recorded in `.rfd/memory.db` (checkpoints table)
**Command**: `rfd checkpoint "message"`
**Purpose**: Save working state that can be reverted to

### Session
A **session** is an active development period focused on a specific feature:
- Has a start and optional end time
- Focuses on one feature at a time
- Maintains context for AI assistants
- Tracks progress and validation state

**Location**: `.rfd/context/current.md` and `.rfd/memory.db`
**Commands**: `rfd session start <feature>`, `rfd session end`
**Purpose**: Maintain focus and context during development

### Session Snapshot
A **session snapshot** is a complete capture of the session state at a point in time:
- Full context dump
- Memory state
- Validation results
- Feature progress
- Timestamp and metadata

**Location**: `.rfd/context/snapshots/` (formerly checkpoints/)
**Created**: Automatically on session end or manually
**Purpose**: Historical record and recovery

### Feature
A **feature** is a discrete unit of functionality:
- Has unique ID
- Has description and acceptance criteria
- Tracks status (pending, building, testing, complete, blocked)
- Can have dependencies on other features

**Location**: Stored in `.rfd/memory.db` (features table)
**Commands**: `rfd feature add`, `rfd feature update`
**Purpose**: Organize work into manageable pieces

### Validation
**Validation** is the process of checking reality:
- File structure rules
- Code execution
- Test passing
- API contracts
- Database state

**Location**: Results in `.rfd/memory.db`, rules in `.rfd/config.yaml`
**Command**: `rfd validate`
**Purpose**: Ensure code matches specification

### Drift
**Drift** occurs when development deviates from specification:
- Adding unspecified features
- Violating constraints
- Exceeding limits
- Breaking acceptance criteria

**Detection**: Automatic during validation
**Prevention**: Checkpoints and validation gates
**Purpose**: Keep development on track

## Data Locations

### `.rfd/memory.db`
SQLite database containing:
- Features table (specifications)
- Checkpoints table (save points)
- Sessions table (development periods)
- Memory table (AI context)

### `.rfd/config.yaml`
Immutable project configuration:
- Stack definition
- Validation rules
- Project constraints
- Basic project info

### `.rfd/context/`
Active session management:
- `current.md` - Active session context
- `memory.json` - AI memory state
- `snapshots/` - Historical session snapshots

### `.rfd/context/current.md`
Auto-generated session context (READ-ONLY):
- Active feature
- Current status
- Required actions
- Session metadata

## Command Flow

### Starting Work
```bash
rfd session start user_auth  # Begin session
# Creates context, updates memory
```

### During Development
```bash
rfd build              # Compile/build
rfd validate           # Check reality
rfd checkpoint "msg"   # Save if passing
```

### Completing Work
```bash
rfd session end        # End session
# Creates snapshot, updates feature status
```

### Recovery
```bash
rfd revert             # Go to last checkpoint
rfd session restore    # Restore from snapshot
```

## State Transitions

### Feature States
```
pending → building → testing → complete
           ↓
         blocked
```

### Session States
```
none → active → ended
         ↓
      suspended
```

### Checkpoint States
```
created → validated → saved
            ↓
          failed
```

## Best Practices

1. **Checkpoint frequently** when code is working
2. **One session per feature** for focus
3. **Validate before checkpoint** to ensure quality
4. **End sessions properly** to create snapshots
5. **Use `rfd dashboard`** to track progress

## Common Misconceptions

❌ **Wrong**: Checkpoints are the same as git commits
✅ **Right**: Checkpoints are validated save points that reference git commits

❌ **Wrong**: Sessions are just for AI
✅ **Right**: Sessions maintain context for both human and AI developers

❌ **Wrong**: Validation is just testing
✅ **Right**: Validation checks all reality constraints including structure, execution, and specifications

❌ **Wrong**: Features must be completed in order
✅ **Right**: Features can be worked on based on dependencies and priorities

## Glossary

- **Acceptance Criteria**: Specific conditions that must be met for a feature to be considered complete
- **Reality Checkpoint**: A validation point that ensures code actually works
- **Session Context**: The current state and focus of development
- **Spec Drift**: Deviation from the defined specification
- **Truth Source**: Database (.rfd/memory.db) for features, config.yaml for configuration