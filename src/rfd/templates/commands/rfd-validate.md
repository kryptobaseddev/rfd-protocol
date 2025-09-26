---
description: Validate project or specific feature against specifications
argument-hint: [feature-id | 'list'] - Examples: cli_refactor, mock_detection, or 'list' to see all
allowed-tools: Bash(rfd validate*, rfd feature*), Read(.rfd/config.yaml), TodoWrite
---

# RFD Validate

Validate the project or a specific feature against RFD specifications.

!if [ "$1" = "list" ] || [ "$1" = "help" ]; then
  echo "📋 Available features to validate:"
  rfd feature list 2>/dev/null | head -10 | sed 's/^/  • /'
  echo ""
  echo "Usage examples:"
  echo "  /rfd-validate              # Validate entire project"
  echo "  /rfd-validate cli_refactor # Validate specific feature"
  echo "  /rfd-validate list         # Show this help"
elif [ -z "$ARGUMENTS" ]; then
  echo "🔍 Validating entire project..."
  rfd validate
  echo ""
  echo "💡 Tip: To validate a specific feature, use: /rfd-validate <feature-id>"
  echo "   Run '/rfd-validate list' to see available features"
else
  echo "🔍 Validating feature: $1"
  rfd validate --feature $1
fi

If validation fails, analyze the failures and create a todo list for fixes.