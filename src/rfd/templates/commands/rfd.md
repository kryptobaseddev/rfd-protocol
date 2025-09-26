---
description: Complete RFD workflow - build, test, validate, and checkpoint
argument-hint: [feature-id]
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), MultiEdit(*), TodoWrite, Grep(*), Glob(*)
---

# RFD Complete Workflow

Execute the complete Reality-First Development workflow for a feature.

## Workflow Steps:

### 1. Check Status
!rfd check

### 2. Start Session (if feature provided)
If a feature ID is provided: `$1`, start a session for it.
!rfd session start $1

### 3. Read Specifications
Read and understand:
- @.rfd/config.yaml - Project configuration
- @.rfd/context/current.md - Current task
- Run `rfd feature list` to see all features

### 4. Build Feature
!rfd build $1

Fix any build errors that occur.

### 5. Run Tests
Find and run relevant tests for the feature.

### 6. Validate
!rfd validate --feature $1

### 7. Checkpoint Success
If validation passes:
!rfd checkpoint "Completed: $1"

### 8. Update Progress
Use `rfd feature complete <feature-id>` if all tests pass.

Track entire workflow in TodoWrite for visibility.