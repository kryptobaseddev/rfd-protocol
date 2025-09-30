#!/usr/bin/env python3
"""Utility CLI commands for RFD."""

from pathlib import Path
import click


def create_claude_md():
    """Create CLAUDE.md configuration for AI assistants"""
    content = """---
# Claude Code Configuration
tools: enabled
memory: .rfd/context/memory.json
---

# RFD Project Assistant

You are operating in a Reality-First Development (RFD) project. Your ONLY job is to make tests pass.

## Critical Rules
1. Read @.rfd/config.yaml for project configuration
2. Check @.rfd/context/current.md for your current task
3. Features are in the database - use `rfd feature list`
4. Run `rfd check` before ANY changes
5. Every code change MUST improve `rfd validate` output
6. NEVER mock data - use real implementations
7. NEVER add features not in the database

## Workflow for Every Response

### 1. Check Current State
```bash
rfd check
```

### 2. Read Context
- @.rfd/config.yaml - Project configuration
- @.rfd/context/current.md - Current feature/task
- Use `rfd feature list` to see all features
- Use `rfd dashboard` to see progress

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
"""
    Path("CLAUDE.md").write_text(content)
