---
description: Create and manage implementation plans
argument-hint: [create|tasks|phases] [feature-id] - Default shows current plans
allowed-tools: Bash(rfd plan*, rfd feature*), Read(specs/*, .rfd/config.yaml), Write(specs/*), TodoWrite
---

# RFD Planning & Task Management

Create and manage implementation plans for features.

!if [ -z "$1" ]; then
  echo "📅 Current Plans & Tasks"
  echo "========================"
  if [ -d "specs" ]; then
    echo -e "\n📁 Available Plans:"
    ls -1 specs/*_plan.md 2>/dev/null | sed 's|specs/||;s|_plan.md||' | sed 's/^/  • /' || echo "  No plans created yet"
  fi
  echo -e "\n📝 Active Tasks:"
  sqlite3 .rfd/memory.db "SELECT feature_id, description, status FROM tasks WHERE status != 'complete' LIMIT 5;" 2>/dev/null | sed 's/^/  • /' || echo "  No active tasks"
  echo ""
  echo "💡 Planning Commands:"
  echo "  • /rfd-plan create <feature-id> - Create implementation plan"
  echo "  • /rfd-plan tasks <feature-id> - Generate task breakdown"
  echo "  • /rfd-plan phases - Define project phases"
elif [ "$1" = "create" ]; then
  if [ -z "$2" ]; then
    echo "❌ Please specify a feature to plan"
    echo ""
    echo "Available features to plan:"
    rfd feature list 2>/dev/null | grep -v complete | head -5 | sed 's/^/  • /'
    echo ""
    echo "Usage: /rfd-plan create <feature-id>"
  else
    echo "📝 Creating implementation plan for: $2"
    rfd plan create $2
    echo ""
    echo "Next: Generate tasks with /rfd-plan tasks $2"
  fi
elif [ "$1" = "tasks" ]; then
  if [ -z "$2" ]; then
    echo "❌ Please specify a feature for task generation"
    echo "Usage: /rfd-plan tasks <feature-id>"
  else
    echo "🔨 Generating tasks for: $2"
    rfd plan tasks $2
    # Create TodoWrite list from generated tasks
    echo ""
    echo "Creating task list for tracking..."
  fi
elif [ "$1" = "phases" ]; then
  echo "📊 Defining project phases..."
  rfd plan phases
elif [ "$1" = "help" ] || [ "$1" = "list" ]; then
  echo "📚 RFD Planning Commands:"
  echo ""
  echo "Plan Management:"
  echo "  /rfd-plan - Show current plans & tasks"
  echo "  /rfd-plan create <feature> - Create implementation plan"
  echo ""
  echo "Task Generation:"
  echo "  /rfd-plan tasks <feature> - Generate task breakdown"
  echo "  /rfd-plan phases - Define project phases"
  echo ""
  echo "Available features to plan:"
  rfd feature list 2>/dev/null | grep -v complete | head -5 | sed 's/^/  • /'
else
  echo "❓ Unknown plan command: $1"
  echo "Run '/rfd-plan help' for available commands"
fi

Based on the plan, create a TodoWrite list for implementation tracking.