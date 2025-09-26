---
description: Setup RFD environment and dependencies
allowed-tools: Bash(*), Read(*), Write(*), Edit(*)
model: claude-3-5-sonnet-20241022
---

# RFD Setup

Setup the RFD (Reality-First Development) protocol environment with all dependencies.

This command will:
1. Create virtual environment
2. Install all dependencies
3. Setup directory structure
4. Fix permissions
5. Verify installation

!python3 setup.py

After setup, initialize the project:
!rfd init