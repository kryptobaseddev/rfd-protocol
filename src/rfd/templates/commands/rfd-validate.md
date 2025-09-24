---
description: Validate project or specific feature against specifications
argument-hint: [--feature feature-id]
allowed-tools: Bash(./rfd validate*), Read(PROJECT.md), TodoWrite
---

# RFD Validate

Validate the project or a specific feature against RFD specifications.

Usage: 
- `/rfd-validate` - Validate entire project
- `/rfd-validate feature-id` - Validate specific feature

!./rfd validate $ARGUMENTS

If validation fails, analyze the failures and create a todo list for fixes.