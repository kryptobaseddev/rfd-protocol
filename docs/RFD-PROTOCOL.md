# Reality-First Development (RFD) Protocol
## Spec-Driven Application Development System

### Executive Summary
RFD Protocol is a **unified** drop-in system that bridges the gap between AI-assisted development and concrete, measurable progress. It addresses SDLC drift by enforcing reality checkpoints that validate actual progress rather than theoretical planning.

### 🚨 Critical Update: Unified Architecture Decision
After extensive analysis, we've determined that **one unified system** serves all users better than progressive tiers. Solo developers need the SAME guardrails as large teams - they have nobody else to catch mistakes.

### Bootstrap Implementation Strategy
Due to the paradox of needing RFD to build RFD, we employ **Progressive Self-Hosting**:
1. Build minimal verification first (`verify.py`)
2. Use it to verify subsequent development
3. Each completed component helps build the next
4. Full system emerges through controlled evolution

### Core Philosophy

#### What Actually Matters
- **Code that runs** > Perfect architecture
- **One working feature** > Ten planned features  
- **Real data** > Mocked responses
- **Automated checks** > Manual reviews

### Problem Statement
Current AI LLM agent development suffers from:
- SDLC drift where both HUMAN (HITL) and AI agents wander without concrete validation
- Disconnected powerful tools (AGENTS.md, CLAUDE.md, GitHub Spec Kit) with no unified bridge
- Lack of reality checkpoints that PROVE progress
- Over-planning without execution validation
- Memory management issues across sessions
- Inconsistent standardization leading to process drift

### System Architecture

#### Core Components

##### 1. Document-Driven Structure
- **CLAUDE.md**: Base project configuration for Claude Code CLI
  - Memory management system
  - Project context and directives
  - '@' file reference support
  - Session persistence
  
- **AGENTS.md**: Multi-level agent definitions
  - Standardized markdown+frontmatter (YAML) format
  - Single schema standard (no variations)
  - Highly parsable by AI agents
  - Based on OpenAI agents.md structure
  - Hierarchical agent definitions at multiple project levels

- **RFD-SPEC.md**: Specification documents
  - GitHub Spec Kit integration
  - Concrete feature definitions
  - Acceptance criteria
  - Reality checkpoints

##### 2. Reality Checkpoint System
- Automated validation points
- Concrete progress indicators
- No advancement without proof
- Hard-coded checkpoints preventing drift
- Course-correction triggers for both HITL and AI

##### 3. Database Management
- Targeted SQLite databases
- Project state tracking
- Session memory persistence
- Checkpoint validation logs
- Progress metrics storage

##### 4. Script Automation
- Single entry point: `rfd` command
- Python-based orchestration
- Strict process enforcement
- No process variation allowed
- Automated document generation
- Programmatic document standardization

### Implementation Strategy

#### Drop-In Compatibility
- Works with ANY new or existing project
- Zero framework dependencies
- Language agnostic
- Minimal file footprint
- GitHub package distribution model

#### File Structure
```
project-root/
├── CLAUDE.md           # Base Claude Code CLI configuration
├── AGENTS.md          # Root agent definitions
├── RFD-PLAN.md        # Active development plan
├── RFD-SPEC.md        # Current specifications
├── .rfd/
│   ├── config.yaml    # RFD configuration
│   ├── checkpoints.db # SQLite checkpoint database
│   ├── memory.db      # Session memory database
│   └── agents/        # Agent-specific configurations
├── specs/             # Specification documents
│   └── *.md          # Feature specifications
└── agents/           # Multi-level agent definitions
    └── *.md          # Component-level agents

```

### Standardization Requirements

#### AGENTS.md Schema (Strict YAML Frontmatter)
```yaml
---
version: 1.0
agent_type: [orchestrator|executor|validator|monitor]
capabilities:
  - capability_1
  - capability_2
dependencies:
  - dependency_1
checkpoints:
  - checkpoint_1
  - checkpoint_2
validation:
  - test_1
  - test_2
---
```

#### Reality Checkpoints
1. **Code Execution**: Must run without errors
2. **Test Passage**: Automated test validation
3. **Data Flow**: Real data processing confirmed
4. **Integration**: Component interaction verified
5. **User Acceptance**: Feature meets specification

### Workflow Process

#### 1. Specification Phase
- Create/update RFD-SPEC.md
- Define concrete acceptance criteria
- Set reality checkpoints
- No advancement without spec approval

#### 2. Implementation Phase
- AI agent reads CLAUDE.md for context
- References AGENTS.md for capabilities
- Executes against RFD-SPEC.md
- Validates at each checkpoint

#### 3. Validation Phase
- Automated checkpoint verification
- Reality proof collection
- Progress metric recording
- Course correction if needed

#### 4. Memory Management
- Session state persistence
- Cross-session context retention
- Checkpoint history tracking
- Progress continuity

### Integration Points

#### Claude Code CLI
- Native CLAUDE.md support
- '@' file reference system
- Built-in model selection
- Session memory management

#### GitHub Spec Kit
- Specification templates
- Acceptance criteria format
- Test-driven development
- Progress tracking

#### OpenAI AGENTS.md
- Agent definition structure
- Capability declarations
- Hierarchical organization
- Multi-level architecture

### Automated Behaviors

#### For HITL (Human In The Loop)
- Specification requirement enforcement
- Checkpoint validation prompts
- Progress visibility dashboards
- Drift detection alerts

#### For AI LLM Agents
- Strict directive following
- Checkpoint-gated progression
- Automatic course correction
- Reality validation loops

### Key Features

#### 1. Strict Process Control
- No veering from defined process
- Hardcoded checkpoint enforcement
- Automated validation gates
- Progress-only advancement

#### 2. Minimal Complexity
- Few files as possible
- Simple, repeatable system
- Quick project scaffolding
- Tech stack agnostic

#### 3. Reality Validation
- Concrete progress proof
- Running code requirement
- Real data processing
- Automated testing

#### 4. Memory Persistence
- SQLite-based storage
- Session continuity
- Context preservation
- Progress tracking

### Python Script Architecture

#### Entry Point: `rfd` Command
```
rfd init          # Initialize RFD in project
rfd spec          # Manage specifications
rfd checkpoint    # Validate checkpoints
rfd agent         # Agent management
rfd validate      # Run reality checks
rfd progress      # Show progress metrics
rfd sync          # Sync across sessions
```

#### Core Modules
- `rfd.core`: Main orchestration
- `rfd.checkpoint`: Validation system
- `rfd.agents`: Agent management
- `rfd.memory`: Session persistence
- `rfd.spec`: Specification handling
- `rfd.validate`: Reality checking

### Benefits

#### For Development Teams
- Eliminated SDLC drift
- Concrete progress tracking
- Automated validation
- Reduced planning overhead

#### For AI Agent Usage
- Clear directive boundaries
- Reality-based progression
- Memory continuity
- Structured workflows

#### For Project Management
- Visible progress metrics
- Specification compliance
- Quality gates enforcement
- Predictable delivery

### Success Metrics

1. **Drift Reduction**: Measured deviation from specifications
2. **Progress Velocity**: Features completed vs planned
3. **Reality Ratio**: Running code vs documentation
4. **Checkpoint Success**: Validation pass rate
5. **Session Continuity**: Memory retention across sessions

### Implementation Priorities (Bootstrap Approach)

#### Stage 1: Minimal Verification ✅ COMPLETE
- Basic Python script (`verify.py`)
- Detect when AI lies about creating files
- Manual execution for immediate use
- **Purpose**: Prevent hallucination while building rest of system

#### Stage 2: Core CLI Structure (CURRENT FOCUS)
- Extract from existing RFD-PLAN.md
- Basic commands: `init`, `check`, `validate`
- PROJECT.md template generation
- **Verification**: Use Stage 1 to verify our work

#### Stage 3: Validation Engine
- File existence checking
- Syntax validation
- Test execution
- **Verification**: Use Stage 2 CLI to validate

#### Stage 4: Session Management
- SQLite state persistence
- Context generation for AI
- Feature tracking
- **Verification**: Use Stage 3 validation

#### Stage 5: Full Integration
- CLAUDE.md generation
- Memory persistence
- Complete workflow
- **Verification**: System validates itself

### Why Unified Over Tiered
- Solo developers have MORE need for guardrails (no team backup)
- Best practices benefit everyone equally
- Complexity comes from fragmentation, not features
- One well-designed system > Five minimal ones

### Constraints & Requirements

- **MUST** be drop-in compatible with any project
- **MUST** use standardized YAML frontmatter (no variations)
- **MUST** enforce reality checkpoints
- **MUST** prevent process drift
- **MUST** integrate with Claude Code CLI
- **MUST** support both new and existing projects
- **MUST** maintain minimal file footprint
- **MUST** provide single entry point (`rfd`)

### Future Considerations

- Multi-agent orchestration
- Distributed checkpoint validation
- Cross-project memory sharing
- Advanced drift detection algorithms
- Real-time progress dashboards
- Integration with CI/CD pipelines

### Conclusion

RFD Protocol bridges the gap between powerful but disconnected tools, creating a unified system that enforces reality-first development. By focusing on concrete checkpoints and automated validation, it ensures that both human developers and AI agents stay on track, producing working code rather than endless documentation.

The system's strength lies in its simplicity, strict standardization, and unwavering focus on proving progress through reality validation rather than theoretical planning.