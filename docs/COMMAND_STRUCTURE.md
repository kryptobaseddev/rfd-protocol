# RFD Command Structure (v5.0 Proposed)

## Problem with Current Structure

The current command structure has become confusing:
- `rfd spec` and `rfd speckit` overlap functionality
- Too many subcommands (17+ top-level commands)
- Not intuitive what to use when
- Users need to remember "speckit" terminology

## Proposed Clean Structure

### Core Principle: Intuitive & Smart

Commands should be grouped logically and work intelligently:
- Running `rfd` alone shows status
- Running `rfd spec` alone shows current spec
- Running `rfd plan` alone shows current plan
- No cryptic errors - always helpful output

### Command Hierarchy

```
rfd
├── init           # Initialize RFD in project
│   --wizard       # Interactive mode
│   --from-prd     # From requirements doc
│   --mode         # greenfield/brownfield
│
├── spec           # Specification management
│   ├── (default)  # Show current spec
│   ├── init       # Create initial spec
│   ├── constitution # Generate principles
│   ├── clarify    # Resolve ambiguities
│   └── validate   # Check completeness
│
├── plan           # Planning & tasks
│   ├── (default)  # Show current plan
│   ├── create     # Create implementation plan
│   ├── tasks      # Generate task breakdown
│   └── phases     # Define project phases
│
├── analyze        # Analysis & validation
│   --scope        # all/spec/tasks/api/tests
│   --format       # text/json
│
├── session        # Development sessions
│   ├── start      # Begin feature work
│   ├── end        # Complete feature
│   └── status     # Current session info
│
├── build          # Build current feature
├── validate       # Validate against spec
├── checkpoint     # Save progress
│
├── check          # Quick status
├── status         # Detailed status
├── dashboard      # Visual progress
│
├── memory         # Context management
│   ├── show       # Display memory
│   └── reset      # Clear memory
│
├── revert         # Revert to checkpoint
└── migrate        # Database migration
```

## Mapping Old to New

| Old Command | New Command | Notes |
|------------|-------------|-------|
| `rfd speckit constitution` | `rfd spec constitution` | Cleaner, no subcommand |
| `rfd speckit specify` | `rfd spec init` | More intuitive name |
| `rfd speckit clarify` | `rfd spec clarify` | Direct under spec |
| `rfd speckit plan` | `rfd plan create` | Logical grouping |
| `rfd speckit tasks` | `rfd plan tasks` | Tasks under planning |
| `rfd spec create` | `rfd spec init` | Consistent with `rfd init` |
| `rfd spec review` | `rfd spec` | Default action |

## Slash Command Alignment

Claude slash commands map directly to CLI:

| Slash Command | CLI Command | Purpose |
|--------------|-------------|---------|
| `/rfd-init` | `rfd init` | Initialize project |
| `/rfd-spec` | `rfd spec` | Specification management |
| `/rfd-plan` | `rfd plan` | Planning & tasks |
| `/rfd-analyze` | `rfd analyze` | Cross-artifact analysis |
| `/rfd-build` | `rfd build` | Build feature |
| `/rfd-validate` | `rfd validate` | Validate implementation |
| `/rfd-check` | `rfd check` | Quick status |

## Benefits of New Structure

1. **Intuitive**: Commands grouped by function
2. **Discoverable**: Running command without args shows help/current state
3. **Clean**: No confusing subcommands like "speckit"
4. **Consistent**: Similar patterns across all commands
5. **Smart**: Intelligent defaults and helpful output

## Implementation Plan

1. Refactor `cli.py` to implement new structure
2. Update all slash commands to align
3. Add intelligent no-arg behavior
4. Update documentation
5. Add migration for existing users

## Example Usage Flow

```bash
# Initialize project
$ rfd init --wizard

# Review specification
$ rfd spec
> Shows PROJECT.md content

# Create implementation plan
$ rfd plan create user_auth
> ✅ Plan created: specs/user_auth_plan.md

# Generate tasks
$ rfd plan tasks user_auth
> ✅ Tasks created: 12 tasks generated

# Start development
$ rfd session start user_auth
$ rfd build
$ rfd validate
$ rfd checkpoint "Login endpoint working"

# Check progress anytime
$ rfd check
> Shows quick status

# Analyze consistency
$ rfd analyze
> Full cross-artifact report
```

This structure is cleaner, more intuitive, and eliminates the confusion around overlapping commands.