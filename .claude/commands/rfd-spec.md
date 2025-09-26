---
description: View and manage project specifications
argument-hint: [constitution|clarify|validate] - Default shows current spec
allowed-tools: Bash(rfd spec*), Read(.rfd/config.yaml, specs/*), Write(specs/*)
---

# RFD Specification Management

View and manage your project specifications.

!if [ -z "$1" ] || [ "$1" = "show" ]; then
  echo "📋 Current Project Specification"
  echo "=================================="
  rfd spec 2>/dev/null || cat .rfd/config.yaml 2>/dev/null | head -50
  echo ""
  echo "💡 Spec Commands:"
  echo "  • /rfd-spec constitution - Generate project principles"
  echo "  • /rfd-spec clarify - Resolve ambiguities"
  echo "  • /rfd-spec validate - Check completeness"
elif [ "$1" = "constitution" ]; then
  echo "📜 Generating Project Constitution..."
  rfd spec constitution
elif [ "$1" = "clarify" ]; then
  echo "🔍 Analyzing for ambiguities..."
  rfd spec clarify
elif [ "$1" = "validate" ]; then
  echo "✅ Validating specification completeness..."
  rfd spec validate
elif [ "$1" = "help" ]; then
  echo "📚 RFD Specification Commands:"
  echo ""
  echo "View & Manage:"
  echo "  /rfd-spec - Show current specification"
  echo "  /rfd-spec validate - Check spec completeness"
  echo ""
  echo "Generate Documents:"
  echo "  /rfd-spec constitution - Generate principles doc"
  echo "  /rfd-spec clarify - Find & resolve ambiguities"
  echo ""
  echo "Related Commands:"
  echo "  /rfd-plan - Create implementation plans"
  echo "  /rfd-analyze - Cross-artifact analysis"
else
  echo "❓ Unknown spec command: $1"
  echo "Run '/rfd-spec help' for available commands"
fi