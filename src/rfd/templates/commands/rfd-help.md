---
description: Show all RFD commands and their usage
allowed-tools: Read(.claude/commands/*)
---

# RFD Help - Available Commands

## Setup & Initialization
- `/rfd-setup` - Setup RFD environment and dependencies
- `/rfd-init` - Initialize a new RFD project

## Core Workflow
- `/rfd` - Complete RFD workflow for a feature
- `/rfd-check` - Check project status and suggest next actions
- `/rfd-build [feature]` - Build a specific feature
- `/rfd-validate [feature]` - Validate project or feature
- `/rfd-fix` - Automatically fix common issues

## Session Management  
- `/rfd-session start [feature]` - Start working on a feature
- `/rfd-session status` - Check current session
- `/rfd-session complete` - Complete current session

## Getting Started

1. Setup environment:
   ```
   /rfd-setup
   ```

2. Initialize project:
   ```
   /rfd-init
   ```

3. Check status:
   ```
   /rfd-check
   ```

4. Work on a feature:
   ```
   /rfd feature-name
   ```

## Tips
- Use `/rfd-check` frequently to understand project state
- Use `/rfd-fix` when encountering issues
- Track work with `/rfd-session` commands
- The `/rfd` command handles the complete workflow automatically