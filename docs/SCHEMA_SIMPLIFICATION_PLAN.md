# RFD Workflow Implementation Plan - REVISED
## Executive Summary & Problem Analysis

### The Real Discovery
After thorough analysis and external review, the core issue is **NOT** database complexity - it's **missing workflow implementation**. The current schema is perfectly designed for the Nexus Protocol SDLC we need.

```yaml
real_state:
  schema_status: "Ready for implementation" 
  empty_tables: "Unimplemented features, not bugs"
  actual_problem: "Missing workflow commands"
  solution: "Implement, don't demolish"
```

### Brain-dump.md Problem → Existing Schema Solutions
The schema already has infrastructure for every brain-dump.md problem:

| Original Problem | Existing Schema Solution | Missing Implementation |
|-----------------|-------------------------|------------------------|
| Context loss during sessions | `git_worktrees` table | `rfd session start/end` commands |
| AI agent coordination chaos | `agent_sessions` + `agent_handoffs` | `rfd handoff <type>` commands |
| No workflow enforcement | `workflow_checkpoints` + `workflow_state` | `rfd phase validate` commands |
| Mock/fake code prevention | Validation infrastructure | Real-time hooks in CLI |
| Squirrel brain scope drift | `workflow_state` locking | Workflow phase enforcement |

## Proposed Solution: Implement Missing Workflow Commands

### Design Philosophy
- **Use Existing Schema**: It's perfectly designed already
- **Implement Missing Commands**: Build the workflow, not new tables
- **Real-time Prevention**: CLI hooks, not database theater
- **Phase Enforcement**: Lock workflow transitions until validated

### Workflow Commands to Implement

#### 1. Session Isolation (Nexus Protocol Core)
```python
# rfd session start <feature_id> <agent_type>
def start_isolated_session(feature_id: str, agent_type: str):
    """Create isolated git worktree for focused development"""
    worktree_path = f".rfd/worktrees/{feature_id}"
    branch_name = f"feature/{feature_id}-{agent_type}"
    
    # Create git worktree
    subprocess.run(["git", "worktree", "add", worktree_path, "-b", branch_name])
    
    # Record in existing git_worktrees table
    conn.execute("""
        INSERT INTO git_worktrees (feature_id, worktree_path, branch_name, status)
        VALUES (?, ?, ?, 'active')
    """, (feature_id, worktree_path, branch_name))
    
    # Start agent session in existing agent_sessions table
    conn.execute("""
        INSERT INTO agent_sessions (agent_type, agent_role, handoff_data)
        VALUES (?, 'coding', json_object('worktree', ?, 'focus', ?))
    """, (agent_type, worktree_path, feature_id))

# rfd session end
def end_session(session_id: int):
    """Clean up worktree and prepare handoff"""
    # Package completion data for handoff
    # Update agent_sessions with handoff_data
    # Mark git_worktrees as ready for review
```

#### 2. Workflow Phase Enforcement  
```python
# rfd phase validate <from_phase> <to_phase>
def validate_phase_transition(feature_id: str, from_phase: str, to_phase: str):
    """Enforce Review→Build→Validate→Test→Fix→Complete cycle"""
    
    required_checks = {
        'build→validate': ['code_compiles', 'no_todos', 'tests_exist'],
        'validate→test': ['validation_passed', 'no_mock_data'], 
        'test→fix': ['tests_run', 'failures_logged'],
        'fix→complete': ['all_tests_pass', 'git_committed']
    }
    
    phase_key = f"{from_phase}→{to_phase}"
    if phase_key in required_checks:
        for check in required_checks[phase_key]:
            if not run_validation_check(feature_id, check):
                raise WorkflowViolation(f"Cannot transition: {check} failed")
    
    # Record in existing workflow_checkpoints table
    conn.execute("""
        INSERT INTO workflow_checkpoints (workflow_id, state, data)
        VALUES (?, ?, ?)
    """, (feature_id, to_phase, json.dumps({"checks_passed": required_checks[phase_key]})))
```

#### 3. Multi-Agent Handoff System
```python  
# rfd handoff <to_agent_type>
def handoff_to_agent(current_session_id: int, to_agent_type: str):
    """Structured handoff between coding→review→fix agents"""
    
    # Get current session from existing agent_sessions table
    session = get_agent_session(current_session_id)
    
    # Package comprehensive handoff data
    handoff_data = {
        "files_changed": get_git_diff(session['handoff_data']['worktree']),
        "completion_claims": extract_completion_claims(session),
        "test_status": run_tests(session['handoff_data']['worktree']),
        "validation_evidence": collect_evidence()
    }
    
    # Record in existing agent_handoffs table
    conn.execute("""
        INSERT INTO agent_handoffs (from_agent_id, to_agent_id, handoff_type, context_data)
        VALUES (?, ?, ?, ?)
    """, (current_session_id, new_agent_id, to_agent_type, json.dumps(handoff_data)))
```

#### 4. Real-time Prevention Hooks
```python
# CLI-level prevention (not database)
def validate_file_write(file_path: str, content: str) -> bool:
    """Real-time validation before any file operation"""
    
    # Mock/placeholder detection
    forbidden_patterns = ['TODO', 'FIXME', 'mock_data', 'placeholder', 'fake_']
    if any(pattern in content for pattern in forbidden_patterns):
        click.echo("❌ BLOCKED: Mock/placeholder content detected")
        return False
        
    # Scope drift detection  
    current_feature = get_current_feature()
    if detect_scope_expansion(content, current_feature):
        click.echo("❌ BLOCKED: Scope drift detected - stay focused on current feature")
        return False
        
    return True

# Wrap all file operations with validation
@validate_content
def write_file(path: str, content: str):
    """Validated file write operation"""
    with open(path, 'w') as f:
        f.write(content)
```

### Implementation Priority

```yaml
immediate_implementation:
  # Core workflow commands (Week 1)
  - rfd session start <feature_id> <agent_type>  # Uses git_worktrees + agent_sessions
  - rfd session end                              # Cleanup and handoff prep
  - rfd handoff <agent_type>                     # Uses agent_handoffs table
  - rfd phase validate <from> <to>               # Uses workflow_checkpoints
  
high_priority:
  # Prevention hooks (Week 2) 
  - CLI file operation hooks                     # Real-time validation
  - Scope drift detection                        # Feature boundary enforcement
  - Mock/placeholder blocking                    # Code quality assurance
  - Completion claim validation                  # Anti-hallucination
  
medium_priority:
  # Enhanced workflow (Week 3-4)
  - rfd workflow status                          # Visual pipeline state
  - rfd agent list                               # Active agent sessions
  - rfd worktree cleanup                         # Maintenance commands
  - rfd phase history                            # Workflow audit trail

schema_status: "No changes needed - implement commands only"
```

## Implementation Strategy

### Phase 1: Command Development (Zero Risk)
```python
# Create new workflow commands module
# src/rfd/workflow_commands.py

class WorkflowCommands:
    """Nexus Protocol workflow implementation using existing schema"""
    
    def __init__(self, db_path: str):
        self.conn = get_db_connection(db_path)
    
    def start_session(self, feature_id: str, agent_type: str):
        """Implement rfd session start using git_worktrees table"""
        # Implementation using existing tables
        pass
        
    def validate_phase(self, from_phase: str, to_phase: str):  
        """Implement rfd phase validate using workflow_checkpoints"""
        # Implementation using existing tables
        pass
        
    def handoff_agent(self, current_session: int, target_agent: str):
        """Implement rfd handoff using agent_handoffs table"""
        # Implementation using existing tables  
        pass
```

### Phase 2: CLI Integration (Low Risk)
```python
# Add workflow commands to existing CLI
# src/rfd/cli.py - extend existing click groups

@rfd.group()
def session():
    """Isolated development sessions using git worktrees"""
    pass

@session.command()
@click.argument('feature_id')
@click.argument('agent_type') 
def start(feature_id: str, agent_type: str):
    """Start isolated session: rfd session start feature_123 coding"""
    workflow = WorkflowCommands(rfd.db_path)
    workflow.start_session(feature_id, agent_type)
    
@session.command()
def end():
    """End current session and prepare handoff"""
    workflow = WorkflowCommands(rfd.db_path)
    workflow.end_current_session()

@rfd.group() 
def phase():
    """Workflow phase management and validation"""
    pass
    
@phase.command()
@click.argument('from_phase')
@click.argument('to_phase') 
def validate(from_phase: str, to_phase: str):
    """Validate phase transition: rfd phase validate build test"""
    workflow = WorkflowCommands(rfd.db_path)
    workflow.validate_phase_transition(from_phase, to_phase)
    
@rfd.command()
@click.argument('agent_type')
def handoff(agent_type: str):
    """Hand off to different agent: rfd handoff review"""
    workflow = WorkflowCommands(rfd.db_path) 
    workflow.handoff_to_agent_type(agent_type)
```

### Phase 3: Prevention Hooks (Controlled)
```python
# Real-time validation hooks for CLI operations
# src/rfd/prevention.py

class PreventionHooks:
    """Real-time prevention system using process-level hooks"""
    
    @staticmethod
    def validate_file_content(content: str, file_path: str) -> tuple[bool, str]:
        """Validate content before writing to prevent issues"""
        
        # Mock/placeholder detection
        mock_patterns = ['TODO', 'FIXME', 'mock_data', 'placeholder', 'fake_']
        for pattern in mock_patterns:
            if pattern in content:
                return False, f"Mock content detected: {pattern}"
                
        # Scope drift detection
        current_feature = get_current_feature()  
        if detect_scope_expansion(content, current_feature):
            return False, "Content appears to be outside current feature scope"
            
        # Completion claim validation
        if validate_completion_claims(content):
            return False, "Unsubstantiated completion claims detected"
            
        return True, "Content validated"
        
    @staticmethod 
    def wrap_file_operations():
        """Wrap standard file operations with validation"""
        import builtins
        original_open = builtins.open
        
        def validated_open(file, mode='r', **kwargs):
            if 'w' in mode or 'a' in mode:  # Writing modes
                # Add validation wrapper
                pass
            return original_open(file, mode, **kwargs)
            
        builtins.open = validated_open
```

### Phase 4: Full Integration (Production)
```python
# Integrate workflow commands into existing RFD operations
# src/rfd/rfd.py - extend core functionality

class RFD:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.workflow = WorkflowCommands(db_path)
        self.prevention = PreventionHooks()
    
    def start_feature_work(self, feature_id: str):
        """Enhanced feature start with session isolation"""
        # Traditional feature start
        self.start_feature(feature_id)
        
        # Add workflow session
        self.workflow.start_session(feature_id, "coding")
        
        # Enable prevention hooks
        self.prevention.wrap_file_operations()
        
    def complete_feature(self, feature_id: str):
        """Enhanced completion with workflow validation"""
        # Validate all phases completed
        self.workflow.validate_complete_workflow(feature_id)
        
        # Traditional completion
        self.complete_feature_traditional(feature_id)
        
        # Clean up worktrees
        self.workflow.cleanup_feature_worktrees(feature_id)
```

### Implementation Benefits
- **Uses existing schema** - No migration risks or data loss
- **Builds missing workflow** - Solves actual brain-dump.md problems  
- **Real-time prevention** - Process hooks, not database theater
- **Gradual rollout** - Add commands incrementally without breaking existing functionality

## Risk Analysis & Mitigation

### Low Risk Factors (All Green!)
1. **No Schema Changes**: Zero risk of data loss or migration failures
2. **Additive Commands**: New functionality doesn't break existing commands  
3. **Gradual Implementation**: Can roll out one command at a time
4. **Existing Infrastructure**: All tables already exist and ready

### Success Metrics

### Technical Metrics
```yaml
implementation_targets:
  new_commands: 4-6 core workflow commands
  schema_changes: 0 (use existing tables)
  downtime: 0 (additive functionality)
  risk_level: "minimal"
  
validation_requirements:
  existing_functionality: 100% preserved
  new_command_testing: Required before release
  workflow_validation: Must prevent actual problems
```

### Behavioral Metrics  
```yaml
nexus_protocol_effectiveness:
  session_isolation: "Git worktrees working"
  agent_handoffs: "Structured context transfer"
  phase_validation: "Workflow enforcement active"
  real_time_prevention: "Mock/drift blocking functional"
  
developer_experience:
  context_preservation: "No more lost work"
  scope_enforcement: "Stay focused on current feature" 
  quality_assurance: "No mock code in commits"
```

## Implementation Timeline

```yaml
week_1_core_commands:
  duration: "1 week"
  deliverables: ["rfd session", "rfd handoff", "rfd phase validate"]
  risk: "minimal"
  effort: "20 hours"
  
week_2_prevention_hooks:
  duration: "1 week"
  deliverables: ["CLI hooks", "content validation", "scope detection"]
  risk: "low"
  effort: "15 hours"
  
week_3_integration:
  duration: "1 week"
  deliverables: ["enhanced rfd commands", "workflow automation"]
  risk: "low"
  effort: "10 hours"
  
total_effort: "45 hours over 3 weeks"
total_risk: "minimal - additive functionality only"
```

## Rollback Strategy

### Immediate Rollback (Any Time)
```bash
# Simply stop using new commands - existing system unaffected
# No schema changes to reverse
# No data to restore
# Zero complexity rollback
```

### The Schema is Already Perfect
No rollback needed - we're building on existing infrastructure that already works.

## Conclusion & Recommendation - REVISED

**The schema is perfect - we need to implement the missing workflow, not rebuild the database.**

### Why This Approach Works
1. **Zero Migration Risk**: No schema changes = no data loss possibility
2. **Existing Infrastructure**: Tables already designed for Nexus Protocol workflow
3. **Additive Implementation**: New commands enhance, don't replace existing functionality
4. **Real Problem Solving**: Addresses actual brain-dump.md issues (context loss, scope drift, AI lying)
5. **Gradual Rollout**: Can implement and test one command at a time

### Why This Must Be Done
1. **Workflow Missing**: Schema exists but workflow commands don't
2. **Prevention Not Detection**: Need real-time hooks, not after-the-fact logging  
3. **Brain-dump.md Unsolved**: Core problems require process enforcement, not table reorganization
4. **Current Schema Ready**: Tables like `git_worktrees`, `agent_sessions`, `workflow_checkpoints` are designed for this

### What We Learned
1. **Table Count ≠ Complexity**: 5 tables have all the data, others are unimplemented features
2. **Schema is Excellent**: Designed exactly for the workflow we need to build
3. **Implementation Gap**: Commands missing, not tables
4. **Prevention > Detection**: Process hooks > database logs

### Next Steps
1. **Start Implementation**: Begin with `rfd session start` command using `git_worktrees` table
2. **Add Prevention Hooks**: CLI-level validation before file operations
3. **Build Workflow Commands**: `rfd handoff`, `rfd phase validate` using existing tables
4. **Test Incrementally**: Each command can be tested independently

**REVISED RECOMMENDATION: IMPLEMENT WORKFLOW, KEEP SCHEMA** 

The existing schema is perfectly designed for solving the actual brain-dump.md problems. We need to build the missing workflow commands, not reorganize the database.