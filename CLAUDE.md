---
# Claude Code Configuration
model: claude-3-5-sonnet-20241022
temperature: 0.2
max_tokens: 4000
tools: enabled
memory: .rfd/context/memory.json
---

# RFD Project Assistant

You are operating in a Reality-First Development (RFD) project. Your ONLY job is to make tests pass.

## Critical Rules
1. Read @PROJECT.md for the specification
2. Check @.rfd/context/current.md for your current task
3. Read @PROGRESS.md for what's already done
4. Run `rfd check` before ANY changes
5. Every code change MUST improve `rfd validate` output
6. NEVER mock data - use real implementations
7. NEVER add features not in @PROJECT.md

## Workflow for Every Response

### 1. Check Current State
```bash
rfd check
```

### 2. Read Context
- @PROJECT.md - What we're building
- @.rfd/context/current.md - Current feature/task
- @PROGRESS.md - What already works

### 3. Write Code
- Minimal code to fix the FIRST failing test
- Complete, runnable code only
- No explanations, just code that works

### 4. Validate
```bash
rfd build && rfd validate
```

### 5. Checkpoint Success
```bash
rfd checkpoint "Fixed: [describe what you fixed]"
```

### 6. Move to Next
Check @.rfd/context/current.md for next failing test. Repeat.

## Your Memory
- Located at @.rfd/context/memory.json
- Automatically loaded/saved
- Remembers what you've tried
- Tracks what works/doesn't

## Never Forget
- You're fixing tests, not designing architecture
- If tests pass, you're done
- If tests fail, fix them
- Reality (passing tests) > Theory (perfect code)
