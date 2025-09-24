---
description: Manage RFD development sessions
argument-hint: [start|status|complete] [feature-id]
allowed-tools: Bash(./rfd session*), Read(.rfd/context/current.md), Write(.rfd/context/current.md), TodoWrite
---

# RFD Session Management

Manage development sessions to maintain context across work.

Usage:
- `/rfd-session start feature-id` - Start working on a feature
- `/rfd-session status` - Check current session
- `/rfd-session complete` - Complete current session

!./rfd session $ARGUMENTS

Update todo list based on session status.