---
description: List all available feature IDs with descriptions - use these in other commands
allowed-tools: Bash(rfd feature*), Read(.rfd/*)
---

# Available RFD Features

Shows all feature IDs you can use with RFD commands.

## Current Features:
!rfd feature list 2>/dev/null | head -20 || echo "No features found. Initialize with: rfd init"

## How to Use Feature IDs:

These feature IDs can be used with:
- `/rfd-validate <feature-id>` - Validate a specific feature
- `/rfd-session start <feature-id>` - Start working on a feature  
- `/rfd-complete <feature-id>` - Mark a feature as complete
- `/rfd-build <feature-id>` - Build a specific feature

## Current Session:
!rfd session status 2>/dev/null | grep "Current feature:" || echo "No active session"

## Examples:
```
/rfd-session start cli_refactor
/rfd-validate mock_detection
/rfd-complete rfd_core_features
```

💡 Tip: Run `/rfd-check` to see overall project status