---
description: Mark a feature as complete (auto-updates PROJECT.md and database)
argument-hint: feature-id
allowed-tools: Bash(./rfd complete*), Read(PROJECT.md)
---

# RFD Complete Feature

Marks a feature as complete and automatically:
- Updates database status
- Syncs PROJECT.md 
- Records completion timestamp
- Validates acceptance criteria

Usage: `/rfd-complete feature-id`

!./rfd complete $1

No more manual PROJECT.md editing!