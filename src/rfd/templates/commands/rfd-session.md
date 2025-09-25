---
description: Manage RFD development sessions  
argument-hint: [start|status|end] [feature-id] - Examples: "start cli_refactor", "status", "end"
allowed-tools: Bash(rfd session*, rfd feature*), Read(.rfd/context/current.md), Write(.rfd/context/current.md), TodoWrite
---

# RFD Session Management

Manage development sessions to maintain context across work.

!# Check current state first
!CURRENT=$(rfd session status 2>&1 | grep "Current feature:" | cut -d: -f2 | xargs)

!if [ "$1" = "start" ]; then
  if [ -z "$2" ]; then
    echo "❌ Please specify a feature to start. Available features:"
    rfd feature list 2>/dev/null | grep -v complete | head -10 | sed 's/^/  • /'
    echo ""
    echo "Usage: /rfd-session start <feature-id>"
  else
    echo "🚀 Starting session for: $2"
    rfd session start $2
    echo ""
    echo "Next steps:"
    echo "  • /rfd-build - Build the feature"
    echo "  • /rfd-validate - Validate implementation"
    echo "  • /rfd-checkpoint - Save progress"
  fi
elif [ "$1" = "status" ] || [ -z "$1" ]; then
  if [ -n "$CURRENT" ]; then
    echo "📍 Active session: $CURRENT"
    rfd session status
    echo ""
    echo "Commands for current session:"
    echo "  • /rfd-build - Build feature"
    echo "  • /rfd-validate $CURRENT - Validate this feature"
    echo "  • /rfd-complete $CURRENT - Mark as complete"
  else
    echo "💤 No active session"
    echo ""
    echo "Start a session with: /rfd-session start <feature-id>"
    echo "Available features:"
    rfd feature list 2>/dev/null | grep -v complete | head -5 | sed 's/^/  • /'
  fi
elif [ "$1" = "end" ] || [ "$1" = "complete" ]; then
  echo "✅ Ending session..."
  rfd session end
else
  echo "❓ Unknown command: $1"
  echo ""
  echo "Available commands:"
  echo "  • /rfd-session start <feature-id> - Start working on a feature"
  echo "  • /rfd-session status - Check current session"
  echo "  • /rfd-session end - End current session"
fi

Update todo list based on session status.