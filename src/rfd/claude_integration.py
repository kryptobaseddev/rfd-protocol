"""
Claude Code Integration for RFD
Automatically sets up Claude commands in any project
"""

from pathlib import Path
from typing import Dict, List


class ClaudeIntegration:
    """Manages Claude Code integration for RFD projects"""

    # Claude command templates
    COMMANDS = {
        "rfd-check.md": """---
description: Check RFD project status
allowed-tools: Bash(rfd check), Read(PROJECT.md)
---

# RFD Status Check

Check project health and next actions.

!rfd check""",
        "rfd-build.md": """---
description: Build current or specified feature
argument-hint: [feature-id]
allowed-tools: Bash(rfd build*), Read(*), Write(*), Edit(*)
---

# RFD Build

Build the specified feature.

!rfd build $1""",
        "rfd-validate.md": """---
description: Validate project against specifications
argument-hint: [--feature feature-id]
allowed-tools: Bash(rfd validate*), Read(PROJECT.md)
---

# RFD Validate

Validate project or specific feature.

!rfd validate $ARGUMENTS""",
        "rfd-complete.md": """---
description: Mark feature as complete (auto-updates PROJECT.md)
argument-hint: feature-id
allowed-tools: Bash(rfd complete*)
---

# RFD Complete Feature

Mark feature complete and auto-sync PROJECT.md.

!rfd complete $1""",
        "rfd-dashboard.md": """---
description: Show project dashboard
allowed-tools: Bash(rfd dashboard)
---

# RFD Dashboard

Display project status, progress, and statistics.

!rfd dashboard""",
        "rfd-session.md": """---
description: Manage development sessions
argument-hint: [start|status|end] [feature-id]
allowed-tools: Bash(rfd session*), TodoWrite
---

# RFD Session

Manage development sessions.

!rfd session $ARGUMENTS""",
        "rfd-checkpoint.md": """---
description: Save project checkpoint
argument-hint: message
allowed-tools: Bash(rfd checkpoint*)
---

# RFD Checkpoint

Save current state with message.

!rfd checkpoint "$ARGUMENTS" """,
        "rfd.md": """---
description: Complete RFD workflow for a feature
argument-hint: feature-id
allowed-tools: Bash(*), Read(*), Write(*), Edit(*), MultiEdit(*), TodoWrite
---

# RFD Complete Workflow

Execute full RFD workflow for a feature.

## Steps:
1. Check status
!rfd check

2. Start session
!rfd session start $1

3. Build feature
!rfd build $1

4. Validate
!rfd validate --feature $1

5. If passing, complete
!rfd complete $1

6. Checkpoint
!rfd checkpoint "Completed $1"

Track all work with TodoWrite.""",
    }

    @classmethod
    def setup_claude_commands(cls, project_root: Path = Path(".")) -> List[str]:
        """Set up Claude commands in a project by copying from templates"""
        commands_dir = project_root / ".claude" / "commands"
        commands_dir.mkdir(parents=True, exist_ok=True)

        # Use templates instead of hardcoded commands
        templates_dir = Path(__file__).parent / "templates" / "commands"

        created = []
        if templates_dir.exists():
            # Copy all command templates
            import shutil

            for template_file in templates_dir.glob("*.md"):
                target_file = commands_dir / template_file.name
                if not target_file.exists():
                    shutil.copy2(template_file, target_file)
                    created.append(template_file.name)
        else:
            # Fallback to hardcoded commands if templates missing
            for filename, content in cls.COMMANDS.items():
                command_file = commands_dir / filename
                if not command_file.exists():
                    command_file.write_text(content)
                    created.append(filename)

        return created

    @classmethod
    def create_claude_config(cls, project_root: Path = Path(".")) -> bool:
        """Create Claude configuration file"""
        claude_dir = project_root / ".claude"
        claude_dir.mkdir(exist_ok=True)

        config_file = claude_dir / "config.yaml"
        if not config_file.exists():
            config_content = """# Claude Code Configuration for RFD Project
version: "1.0"
project_type: "rfd"

# RFD specific settings
rfd:
  auto_validate: true
  auto_checkpoint: true
  require_tests: true

# Available commands (see .claude/commands/)
commands:
  - rfd-check: Check project status
  - rfd-build: Build features
  - rfd-validate: Validate specifications
  - rfd-complete: Mark features complete
  - rfd-dashboard: View project dashboard
  - rfd-session: Manage sessions
  - rfd-checkpoint: Save checkpoints
  - rfd: Complete workflow automation
"""
            config_file.write_text(config_content)
            return True
        return False

    @classmethod
    def generate_claude_md(cls, project_root: Path = Path(".")) -> bool:
        """Generate CLAUDE.md instructions file"""
        claude_md = project_root / "CLAUDE.md"

        if not claude_md.exists():
            content = """# Claude Code Assistant Instructions

You are working in an RFD (Reality-First Development) project.

## Core Principles
1. **Reality First**: Test and validate everything
2. **No Hallucination**: Only claim what's proven
3. **Specification Driven**: Follow PROJECT.md strictly
4. **Automatic Tracking**: Use database, not manual edits

## Workflow
1. Check status: `/rfd-check`
2. Start work: `/rfd-session start <feature>`
3. Build: `/rfd-build <feature>`
4. Validate: `/rfd-validate`
5. Complete: `/rfd-complete <feature>`

## Important
- Never manually edit PROJECT.md status fields
- Use `/rfd-complete` to mark features done
- Always validate before completing
- Track work with TodoWrite

## Available Commands
See `.claude/commands/` for all slash commands.
"""
            claude_md.write_text(content)
            return True
        return False

    @classmethod
    def full_setup(cls, project_root: Path = Path(".")) -> Dict[str, List[str]]:
        """Complete Claude integration setup"""
        results = {
            "commands": cls.setup_claude_commands(project_root),
            "config": cls.create_claude_config(project_root),
            "instructions": cls.generate_claude_md(project_root),
        }
        return results
