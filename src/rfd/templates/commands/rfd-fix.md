---
description: Automatically fix common RFD issues
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), MultiEdit(*), TodoWrite
model: claude-3-5-sonnet-20241022
---

# RFD Auto-Fix

Automatically detect and fix common RFD issues:
- Virtual environment problems
- Missing dependencies
- Linting errors
- Build failures
- Test failures

## 1. Check current status
!rfd check

## 2. Fix environment issues
!python3 setup.py

## 3. Fix linting issues
!ruff check . --fix --unsafe-fixes

## 4. Run tests and fix failures
Analyze test failures and fix them systematically.

## 5. Validate fixes
!rfd validate

Track all fixes in todo list for visibility.