# CLAUDE.md - Claude Code CLI Configuration

## Project Overview
This is a Reality-First Development (RFD) Protocol project that enforces spec-driven development with concrete reality checkpoints. The system prevents SDLC drift by validating actual progress rather than theoretical planning.

## Core Principles
1. **Reality First**: Code that runs > Perfect architecture
2. **Feature Focus**: One working feature > Ten planned features
3. **Real Data**: Real data > Mocked responses
4. **Automation**: Automated checks > Manual reviews

## Project Structure
```
@RFD-PROTOCOL.md     # Complete system documentation
@RFD-PLAN.md         # Active development roadmap
@AGENTS.md           # Agent orchestration definitions
@RFD-SPEC.md         # Current specifications (when created)
```

## Reality Checkpoints
You MUST validate these checkpoints before advancing:
1. ✓ Specification complete with acceptance criteria
2. ✓ Code executes without errors
3. ✓ Tests pass (unit, integration, acceptance)
4. ✓ Real data flows through the system
5. ✓ Integration verified between components
6. ✓ User acceptance confirmed

## Development Workflow

### 1. Always Start With Specification
- Check @RFD-SPEC.md for current requirements
- Validate acceptance criteria are concrete
- Ensure checkpoints are defined
- NO implementation without specification

### 2. Implementation Rules
- Write code that RUNS first
- Create tests that VALIDATE reality
- Use REAL data, not mocks
- Build ONE feature completely before starting another

### 3. Validation Requirements
- Every change must pass ALL checkpoints
- No theoretical progress - PROVE it works
- Document reality, not intentions
- Checkpoint failures BLOCK advancement

## Agent Directives

### For Implementation Tasks
1. Read specification from @RFD-SPEC.md
2. Implement minimum viable solution that RUNS
3. Validate against reality checkpoints
4. Only proceed if checkpoint passes
5. Update progress in checkpoint database

### For Validation Tasks
1. Execute code to verify it runs
2. Run test suites for verification
3. Process real data through system
4. Verify component integration
5. Document validation results

### For Planning Tasks
1. Reference @RFD-PLAN.md for roadmap
2. Break down into concrete, testable chunks
3. Define reality checkpoints for each chunk
4. Create specifications before implementation
5. Update plan based on reality feedback

## Memory Management

### Session Persistence
- Current specification being implemented
- Last validated checkpoint
- Active feature under development
- Test results from last run
- Integration status

### Cross-Session Context
- Checkpoint history
- Specification evolution
- Progress metrics
- Drift incidents
- Validation patterns

## File References

### Critical Files
- @RFD-PROTOCOL.md - System documentation
- @RFD-PLAN.md - Development roadmap
- @AGENTS.md - Agent definitions
- @.rfd/config.yaml - RFD configuration
- @.rfd/checkpoints.db - Checkpoint database

### Specification Files
- @specs/*.md - Feature specifications
- @RFD-SPEC.md - Current active spec

### Agent Files
- @agents/*.md - Component-level agents

## Constraints & Requirements

### MUST Rules
- MUST validate reality checkpoints
- MUST have running code before advancing
- MUST use real data for validation
- MUST block on checkpoint failure
- MUST maintain session memory

### NEVER Rules
- NEVER skip checkpoints
- NEVER accept theoretical progress
- NEVER use mocked validation
- NEVER proceed without specification
- NEVER lose session context

## Command Integration

### RFD Commands
When implementing features, use these commands:
- `rfd checkpoint` - Validate current checkpoint
- `rfd validate` - Run reality checks
- `rfd progress` - Show progress metrics
- `rfd spec` - Manage specifications

### Validation Commands
Always run these before marking complete:
- Test execution commands
- Linting and type checking
- Integration tests
- Data flow verification

## Error Handling

### On Checkpoint Failure
1. STOP progression immediately
2. Document failure reason
3. Identify correction needed
4. Implement fix
5. Re-validate checkpoint

### On Drift Detection
1. Compare against specification
2. Identify deviation point
3. Course-correct to specification
4. Validate correction
5. Update drift metrics

## Progress Tracking

### What Constitutes Progress
- ✓ Code that executes successfully
- ✓ Tests that pass consistently
- ✓ Data that flows correctly
- ✓ Features that meet specifications
- ✗ Documentation without code
- ✗ Plans without implementation
- ✗ Tests without execution

## Integration Points

### GitHub Spec Kit
- Use for specification format
- Follow acceptance criteria structure
- Maintain test-driven approach

### AGENTS.md Structure
- Reference for agent capabilities
- Use for task delegation
- Follow hierarchical organization

### SQLite Databases
- Track checkpoint validations
- Store progress metrics
- Maintain session memory

## Quality Gates

### Before Committing
1. All checkpoints validated
2. Tests passing
3. Real data processed
4. Integration verified
5. Specification met

### Before Marking Complete
1. User acceptance achieved
2. Production ready
3. Documentation accurate
4. Metrics recorded
5. Memory persisted

## Success Metrics

Track these for every session:
- Checkpoints passed vs failed
- Features completed vs started
- Real data validations
- Drift incidents
- Session continuity

## Notes for Claude

Remember: You are enforcing Reality-First Development. Every action must be validated against reality. No theoretical progress is acceptable. Always validate checkpoints before proceeding. Maintain session memory for continuity. Focus on working code over perfect documentation.