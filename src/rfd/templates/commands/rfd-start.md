---
description: Start RFD session - comprehensive project overview and planning
allowed-tools: Bash(*), Read(*), TodoWrite, Grep(*)
---

# RFD Start - Begin Development Session

Complete session initialization with full context.

## 1. Project Overview
!echo "=== RFD PROJECT OVERVIEW ==="
@.rfd/config.yaml
!rfd dashboard

## 2. Check Current Context
!echo -e "\n=== CURRENT CONTEXT ==="
@.rfd/context/current.md
@.rfd/context/memory.json

## 3. Show Test Status
!echo -e "\n=== TEST STATUS ==="
!python -m pytest tests/ --co -q 2>&1 | tail -5

## 4. List Pending Work
!echo -e "\n=== PENDING FEATURES ==="
!sqlite3 .rfd/memory.db "SELECT id, description, status FROM features WHERE status != 'complete';"

## 5. Show Recent Progress
!echo -e "\n=== RECENT PROGRESS ==="
!sqlite3 .rfd/memory.db "SELECT timestamp, message FROM checkpoints ORDER BY timestamp DESC LIMIT 10;"

## 6. Suggest Plan
Based on above, create a TodoWrite list with:
- Current feature to work on
- Specific tasks to complete
- Tests to run
- Validation steps

## 7. Ready Check
"Ready to begin? Use `/rfd-session start <feature>` to start working."