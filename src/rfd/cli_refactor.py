"""
Proposed RFD Command Structure Refactor

CURRENT PROBLEMS:
1. `rfd speckit` subcommands duplicate `rfd spec` functionality
2. Too many commands causing confusion
3. Not intuitive what to use when

PROPOSED SOLUTION:
Merge speckit functionality directly into main RFD commands
"""

# BEFORE (Confusing):
"""
rfd spec create              # Interactive spec creation
rfd spec review              # Review specification
rfd speckit constitution     # Create project constitution
rfd speckit specify         # Define detailed specifications
rfd speckit clarify        # Identify ambiguities
rfd speckit plan           # Create implementation plan
rfd speckit tasks          # Generate task breakdown
"""

# AFTER (Clean & Intuitive):
"""
=== SPECIFICATION COMMANDS ===
rfd spec                    # Review current specification (alias: rfd spec review)
rfd spec init              # Create initial specification (was: rfd spec create)
rfd spec constitution      # Generate immutable principles (was: rfd speckit constitution)
rfd spec clarify          # Identify & resolve ambiguities (was: rfd speckit clarify)

=== PLANNING COMMANDS ===
rfd plan                   # Create implementation plan (was: rfd speckit plan)
rfd plan tasks            # Generate task breakdown (was: rfd speckit tasks)
rfd plan phases           # Define project phases

=== ANALYSIS COMMANDS ===
rfd analyze               # Cross-artifact consistency check
rfd analyze spec          # Analyze specification coverage
rfd analyze drift         # Check for scope drift

=== CORE WORKFLOW ===
rfd init                  # Initialize RFD in project
rfd session start        # Start working on feature
rfd build                # Build current feature
rfd validate            # Validate implementation
rfd checkpoint          # Save progress
rfd session end         # Complete feature

=== STATUS & REVIEW ===
rfd check               # Quick status check
rfd status              # Detailed project status
rfd dashboard           # Visual progress dashboard
rfd memory              # Show/manage context memory

=== STATE MANAGEMENT ===
rfd revert              # Revert to last checkpoint
rfd migrate             # Migrate database after update
"""

# INTELLIGENT COMMAND ROUTING:
"""
When user runs a command, RFD should be smart:

1. `rfd spec` with no args → Show current spec (don't error)
2. `rfd plan` with no args → Show current plan or generate if none
3. `rfd analyze` with no args → Run full analysis
4. `rfd` with no args → Show status (like `rfd check`)

This makes it more intuitive - users can explore by just typing commands.
"""

# SLASH COMMAND ALIGNMENT:
"""
Claude slash commands should map directly:

/rfd-init       → rfd init
/rfd-spec       → rfd spec
/rfd-plan       → rfd plan
/rfd-build      → rfd build
/rfd-validate   → rfd validate
/rfd-analyze    → rfd analyze
/rfd-check      → rfd check

No more /rfd-speckit-* commands needed!
"""
