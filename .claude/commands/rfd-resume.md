---
description: Resume RFD work - shows status, context, and continues where you left off
allowed-tools: Bash(*), Read(.rfd/context/current.md, .rfd/context/memory.json, .rfd/config.yaml), TodoWrite
---

# RFD Resume - Continue Where You Left Off

This command performs comprehensive session recovery:
1. Loads last session context and memory
2. Shows project status, gaps, and progress
3. Checks for unresolved issues and blockers
4. Suggests next actions based on gaps and priorities

## 1. Load Full Context
@.rfd/context/current.md
@.rfd/context/memory.json
@.rfd/config.yaml

## 2. System Health Check
!rfd check
!rfd migrate  # Check for pending migrations
!rfd upgrade-check  # Check if RFD needs updating

## 3. Show Comprehensive Status
!rfd dashboard
!rfd gaps  # Show critical gaps and missing features
!rfd session status
!rfd workflow status  # Check workflow enforcement status

## 4. Analyze Gaps and Priorities
Based on `rfd gaps` output:
- Identify critical gaps (🚨 priority)
- Check partial implementations (⚠️)
- Note what's already solved (✅)
- Focus on highest priority missing items

## 5. Create Action Plan
Create TodoWrite list based on:
1. Critical gaps that block progress
2. Current session/feature if active
3. Missing workflow enforcement items
4. Unresolved queries from `rfd workflow status`

## 6. Suggest Workflow Commands
Based on gaps, suggest proper commands:
- `rfd workflow start <feature>` - For new features with enforcement
- `rfd session start <feature> --isolate` - For isolated git worktree work
- `rfd analyze` - For cross-artifact validation
- `rfd audit` - For database-first compliance check

## 7. Ask Strategic Question
"Based on gap analysis:
- 46.2% gaps solved, 46.2% still missing
- Critical missing: [list top 3]

Should we:
1. Address critical gaps first?
2. Continue with existing features?
3. Start workflow-enforced development?

What's your priority today?"