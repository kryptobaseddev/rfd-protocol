---
description: Check RFD project status and suggest next actions
allowed-tools: Bash(rfd check, rfd session*, rfd feature*), Read(*), TodoWrite
---

# RFD Status Check

Check the current status of your RFD project and get suggestions for next actions.

!echo "🔍 Checking RFD Project Status..."
!echo "================================"
!rfd check

!echo -e "\n📊 Feature Summary:"
!PENDING=$(rfd feature list 2>/dev/null | grep -c "pending" || echo "0")
!IN_PROGRESS=$(rfd feature list 2>/dev/null | grep -c "in_progress\|building" || echo "0")
!COMPLETE=$(rfd feature list 2>/dev/null | grep -c "complete" || echo "0")
!echo "  • Pending: $PENDING"
!echo "  • In Progress: $IN_PROGRESS"
!echo "  • Complete: $COMPLETE"

!echo -e "\n💡 Suggested Next Actions:"
!CURRENT=$(rfd session status 2>&1 | grep "Current feature:" | cut -d: -f2 | xargs)
!if [ -n "$CURRENT" ]; then
  echo "  ✓ Continue working on: $CURRENT"
  echo "    - Run: /rfd-build"
  echo "    - Run: /rfd-validate $CURRENT"
else
  if [ "$IN_PROGRESS" -gt "0" ]; then
    echo "  ✓ Resume an in-progress feature:"
    rfd feature list 2>/dev/null | grep -E "in_progress|building" | head -3 | sed 's/^/    - /'
    echo "    - Run: /rfd-session start <feature-id>"
  elif [ "$PENDING" -gt "0" ]; then
    echo "  ✓ Start a new feature:"
    rfd feature list 2>/dev/null | grep "pending" | head -3 | sed 's/^/    - /'
    echo "    - Run: /rfd-session start <feature-id>"
  else
    echo "  ✓ All features complete! 🎉"
    echo "    - Review with: /rfd-dashboard"
    echo "    - Add new features: /rfd-spec"
  fi
fi

!echo -e "\n🛠️ Quick Commands:"
!echo "  • /rfd-features - List all features"
!echo "  • /rfd-quick-ref - Full command reference"
!echo "  • /rfd-help - Get help"

Based on the status, suggest and track next actions using TodoWrite.