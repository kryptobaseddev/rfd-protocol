---
description: Manage project specifications and constitution
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), MultiEdit(*)
---

# RFD Spec - Specification Management

Create and manage project specifications, constitution, and acceptance criteria.

## Commands

### Review current specification
!rfd spec

### Create project constitution (immutable principles)
!rfd spec constitution

### Identify specification ambiguities
!rfd spec clarify

### Validate specification completeness
!rfd spec validate

## Workflow

1. Review PROJECT.md specification
@PROJECT.md

2. Check for ambiguities
!rfd spec clarify

3. Generate constitution if needed
!rfd spec constitution

4. Validate completeness
!rfd spec validate

The specification is the single source of truth for what can be built.