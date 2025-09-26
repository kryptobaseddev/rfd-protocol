---
description: Analyze and track RFD system gaps - shows what's missing, partial, or solved
allowed-tools: Bash(*), Read(.rfd/memory.db, src/rfd/*.py), TodoWrite, MultiEdit
---

# RFD Gaps - Track System Completion Status

This command provides comprehensive gap analysis and tracking.

## 1. Show Current Gap Status
!rfd gaps

## 2. Analyze Gap Categories
Group gaps by:
- Priority: 🚨 critical, 🔴 high, 🟡 medium
- Status: ❌ missing, ⚠️ partial, ✅ solved
- Category: core_problems, critical_missing

## 3. Calculate Real Progress
From `rfd gaps` output, calculate:
- % Solved (should be 46.2% currently)
- % Partial (should be 7.7% currently) 
- % Missing (should be 46.2% currently)

## 4. Identify Blockers
List critical gaps that block other features:
1. Real-time Workflow Enforcement - Can't prevent deviation
2. Multi-Agent Coordination - Can't parallelize work
3. Scope Drift Prevention - Can't stay on track
4. AI Hallucination Prevention - Only detects after-the-fact

## 5. Create Gap-Closing Plan
For each missing critical gap, create TodoWrite items:
- What needs to be implemented
- Which files need modification
- How to validate it works

## 6. Check for New Gaps
!rfd analyze  # Cross-artifact validation might reveal new gaps

## 7. Suggest Next Gap to Address
Based on priority and dependencies, recommend:
"Most critical gap to address: [gap name]
This would unlock: [benefits]
Estimated effort: [assessment]"