---
description: Quick reference guide for all RFD commands and current project state
allowed-tools: Bash(rfd*), Read(.rfd/*, .rfd/config.yaml)
---

# RFD Quick Reference Guide

## 🎯 Current State
!echo "=== CURRENT PROJECT STATE ==="
!rfd check 2>&1 | tail -n +2

## 📦 Available Features
!echo -e "\n=== FEATURES (use these IDs in commands) ==="
!rfd feature list 2>/dev/null | head -10 | sed 's/^/  /'

## 🛠️ Essential Commands

### Getting Started
- `/rfd-init` - Initialize RFD in your project
- `/rfd-features` - List all feature IDs
- `/rfd-check` - Quick project status

### Working on Features  
- `/rfd-session start <feature-id>` - Begin working on a feature
- `/rfd-build` - Build current feature
- `/rfd-validate [feature-id]` - Validate project or specific feature
- `/rfd-complete <feature-id>` - Mark feature as complete

### Planning & Specs
- `/rfd-spec` - View/manage specifications
- `/rfd-plan` - Create implementation plans
- `/rfd-analyze` - Analyze project consistency

### Progress Tracking
- `/rfd-status` - Detailed project status
- `/rfd-dashboard` - Visual progress overview
- `/rfd-checkpoint <message>` - Save progress point

## 💡 Pro Tips
1. Run commands without arguments to see current state
2. Use `/rfd-features` to discover valid feature IDs
3. Always `/rfd-check` before starting work
4. Save progress with `/rfd-checkpoint` regularly

## 📝 Current Session
!rfd session status 2>/dev/null || echo "No active session. Start with: /rfd-session start <feature-id>"