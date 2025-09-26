---
description: Build the current RFD feature
argument-hint: [feature-id]
allowed-tools: Bash(rfd build*), Read(*), Write(*), Edit(*), TodoWrite
---

# RFD Build Feature

Build the specified feature or current feature.

Usage: `/rfd-build [feature-id]`

!rfd build $ARGUMENTS

After building, run validation:
!rfd validate --feature $1