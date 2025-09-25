---
description: Resume RFD work - shows status, context, and continues where you left off
allowed-tools: Bash(*), Read(.rfd/context/current.md, .rfd/context/memory.json, PROJECT.md), TodoWrite
---

# RFD Resume - Continue Where You Left Off

This command automatically:
1. Loads your last session context
2. Shows project status and progress
3. Displays current phase and tasks
4. Suggests next actions

## Load Context
@.rfd/context/current.md
@.rfd/context/memory.json
@.rfd/config.yaml

## Check Status
!./rfd-new dashboard

## Show Current Session
!./rfd-new session status

## Display Next Actions
Based on the context, suggest next steps and create a TodoWrite list.

## Ask to Continue
"Ready to continue with [current feature]? Or would you like to switch to something else?"