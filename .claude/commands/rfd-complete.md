---
description: Mark a feature as complete (updates database)
argument-hint: <feature-id | 'list'> - Example: cli_refactor, or 'list' to see features
allowed-tools: Bash(rfd complete*, rfd feature*), Read(.rfd/config.yaml)
---

# RFD Complete Feature

Marks a feature as complete and automatically:
- Updates database status
- Updates database 
- Records completion timestamp
- Validates acceptance criteria

!if [ "$1" = "list" ] || [ "$1" = "help" ]; then
  echo "📋 Features that can be marked complete:"
  rfd feature list 2>/dev/null | grep -v "complete" | head -10 | sed 's/^/  • /'
  echo ""
  echo "Usage: /rfd-complete <feature-id>"
  echo "Example: /rfd-complete cli_refactor"
elif [ -z "$1" ]; then
  echo "❌ Please specify a feature to complete"
  echo ""
  echo "In-progress features:"
  rfd feature list 2>/dev/null | grep -E "building|in_progress" | head -5 | sed 's/^/  • /'
  echo ""
  echo "Usage: /rfd-complete <feature-id>"
  echo "   Or: /rfd-complete list (to see all features)"
else
  echo "✅ Marking feature as complete: $1"
  rfd complete $1
  echo ""
  echo "🎉 No more manual .rfd/config.yaml editing!"
fi