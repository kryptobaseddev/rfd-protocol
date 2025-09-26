"""
Context Manager for RFD
Handles programmatic context file generation and updates.
These files are READ-ONLY for AI agents, WRITE-ONLY for RFD system.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class ContextManager:
    """
    Manages .rfd/context files programmatically.

    IMPORTANT: These files are:
    - Generated automatically by RFD commands
    - Read-only for AI/LLM agents
    - Should NEVER be manually edited
    """

    def __init__(self, rfd_dir: Path):
        self.rfd_dir = rfd_dir
        self.context_dir = rfd_dir / "context"
        self.context_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.current_file = self.context_dir / "current.md"
        self.memory_file = self.context_dir / "memory.json"

        # Add warning headers to files
        self._ensure_readonly_headers()

    def _ensure_readonly_headers(self):
        """Add warnings to context files about not editing them manually"""
        warning = "AUTO-GENERATED FILE - DO NOT EDIT MANUALLY"

        # Check current.md
        if self.current_file.exists():
            content = self.current_file.read_text()
            if warning not in content:
                # Prepend warning as HTML comment
                content = f"<!-- {warning} -->\n{content}"
                self.current_file.write_text(content)

    def update_current_session(
        self,
        session_id: int,
        feature_id: str,
        status: str,
        feature_data: Dict[str, Any],
        validation_results: Optional[Dict] = None,
    ):
        """
        Update current.md with session information.
        Called by rfd session start/end commands.
        """
        started = datetime.now().isoformat()

        content = f"""<!-- AUTO-GENERATED FILE - DO NOT EDIT MANUALLY -->
---
session_id: {session_id}
feature: {feature_id}
started: {started}
status: {status}
---

# Current Session: {feature_id}

## Feature Specification
{feature_data.get("description", "No description")}

**Acceptance Criteria:**
{feature_data.get("acceptance_criteria", "Not specified")}

## Current Status
"""

        if validation_results:
            content += "```\n"
            content += f"rfd validate --feature {feature_id}\n"
            for result in validation_results.get("results", []):
                icon = "✅" if result["passed"] else "❌"
                content += f"{icon} {result['test']}: {result['message']}\n"
            content += "```\n"

        content += """
## Required Actions
1. Make all validation tests pass
2. Ensure code follows .rfd/config.yaml constraints
3. No mocks - use real implementations

## Commands
```bash
rfd build          # Build current feature
rfd validate       # Check if tests pass
rfd checkpoint     # Save working state
```

## Constraints from .rfd/config.yaml
- NO new features until 100% tests pass
- MUST use RFD workflow for all fixes
- MUST validate each fix with tests
- NO mock data in tests
- MUST maintain backward compatibility
"""

        self.current_file.write_text(content)

    def update_memory(self, data: Dict[str, Any]):
        """
        Update memory.json with session memory.
        Called programmatically by RFD system.
        """
        # Add metadata
        data["_metadata"] = {
            "updated": datetime.now().isoformat(),
            "warning": "AUTO-GENERATED - DO NOT EDIT",
            "managed_by": "rfd.context_manager",
        }

        with open(self.memory_file, "w") as f:
            json.dump(data, f, indent=2)

    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Read current session context (safe for AI to read)"""
        if not self.current_file.exists():
            return None

        import frontmatter

        with open(self.current_file) as f:
            post = frontmatter.load(f)
            return {"metadata": post.metadata, "content": post.content}

    def get_memory(self) -> Dict[str, Any]:
        """Read memory context (safe for AI to read)"""
        if not self.memory_file.exists():
            return {}

        with open(self.memory_file) as f:
            return json.load(f)

    def clear_session(self):
        """Clear current session when ending"""
        if self.current_file.exists():
            # Don't delete, just mark as ended
            content = self.current_file.read_text()
            content = content.replace("status: building", "status: ended")
            self.current_file.write_text(content)

    def create_handoff(self, session_data: Dict[str, Any]) -> str:
        """Create handoff document for session continuation"""
        handoff = f"""<!-- AUTO-GENERATED HANDOFF - DO NOT EDIT -->
# Session Handoff

## Last Session
- Feature: {session_data.get("feature_id", "unknown")}
- Started: {session_data.get("started_at", "unknown")}
- Status: {session_data.get("status", "unknown")}

## Completed Work
{json.dumps(session_data.get("completed_tasks", []), indent=2)}

## Next Steps
1. Run `rfd resume` to load context
2. Run `rfd check` to see current state
3. Continue with next feature

## Important Files
- Config: .rfd/config.yaml
- Database: .rfd/memory.db
- Context: .rfd/context/ (READ-ONLY for AI)
"""

        handoff_file = self.context_dir / "handoff.md"
        handoff_file.write_text(handoff)
        return str(handoff_file)
