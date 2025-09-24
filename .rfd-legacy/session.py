"""
Session Manager for RFD
Manages development sessions and AI context
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, Optional


class SessionManager:
    def __init__(self, rfd):
        self.rfd = rfd
        self.current_session = None
        self.context_dir = rfd.rfd_dir / "context"

    def start(self, feature_id: str) -> int:
        """Start new development session"""
        # End any existing session
        if self.current_session:
            self.end(success=False)

        # Create new session
        conn = sqlite3.connect(self.rfd.db_path)
        cursor = conn.execute(
            """
            INSERT INTO sessions (started_at, feature_id)
            VALUES (?, ?)
        """,
            (datetime.now().isoformat(), feature_id),
        )
        session_id = cursor.lastrowid
        conn.commit()

        self.current_session = {
            "id": session_id,
            "feature_id": feature_id,
            "started_at": datetime.now().isoformat(),
        }

        # Update feature status
        conn.execute(
            """
            UPDATE features SET status = 'building'
            WHERE id = ?
        """,
            (feature_id,),
        )
        conn.commit()

        # Generate context for AI
        self._generate_context(feature_id)

        return session_id

    def end(self, success: bool = True) -> Optional[int]:
        """End current session"""
        if not self.current_session:
            return None

        session_id = self.current_session["id"]

        # Update session record
        conn = sqlite3.connect(self.rfd.db_path)
        conn.execute(
            """
            UPDATE sessions
            SET ended_at = ?, success = ?
            WHERE id = ?
        """,
            (datetime.now().isoformat(), success, session_id),
        )

        # Update feature status if successful
        if success:
            conn.execute(
                """
                UPDATE features SET status = 'complete', completed_at = ?
                WHERE id = ?
            """,
                (datetime.now().isoformat(), self.current_session["feature_id"]),
            )

        conn.commit()

        self.current_session = None
        return session_id

    def get_current(self) -> Optional[Dict[str, Any]]:
        """Get current session info"""
        return self.current_session

    def get_current_feature(self) -> Optional[str]:
        """Get current feature being worked on"""
        if self.current_session:
            return self.current_session["feature_id"]

        # Check for any in-progress features
        conn = sqlite3.connect(self.rfd.db_path)
        result = conn.execute("""
            SELECT id FROM features
            WHERE status = 'building'
            ORDER BY created_at DESC LIMIT 1
        """).fetchone()

        return result[0] if result else None

    def suggest_next_action(self) -> str:
        """Suggest next action based on current state"""
        state = self.rfd.get_current_state()

        # Check validation status
        if not state["validation"]["passing"]:
            return "./rfd validate  # Fix validation errors"

        # Check build status
        if not state["build"]["passing"]:
            return "./rfd build  # Fix build errors"

        # Check for pending features
        conn = sqlite3.connect(self.rfd.db_path)
        pending = conn.execute("""
            SELECT id FROM features
            WHERE status = 'pending'
            ORDER BY created_at LIMIT 1
        """).fetchone()

        if pending:
            return f"./rfd session start {pending[0]}"

        return "./rfd check  # All features complete!"

    def _generate_context(self, feature_id: str):
        """Generate context file for AI"""
        spec = self.rfd.load_project_spec()

        # Find feature
        feature = None
        for f in spec.get("features", []):
            if f["id"] == feature_id:
                feature = f
                break

        if not feature:
            return

        # Get current validation status
        validation = self.rfd.validator.validate(feature=feature_id)

        # Generate context document
        context = f"""---
session_id: {self.current_session["id"]}
feature: {feature_id}
started: {self.current_session["started_at"]}
status: building
---

# Current Session: {feature_id}

## Feature Specification
{feature["description"]}

**Acceptance Criteria:**
{feature.get("acceptance", "Not specified")}

## Current Status
```
./rfd validate --feature {feature_id}
"""

        # Add validation results
        for result in validation["results"]:
            icon = "✅" if result["passed"] else "❌"
            context += f"{icon} {result['test']}: {result['message']}\n"

        context += """```

## Required Actions
1. Make all validation tests pass
2. Ensure code follows PROJECT.md constraints
3. No mocks - use real implementations

## Commands
```bash
./rfd build          # Build current feature
./rfd validate       # Check if tests pass
./rfd checkpoint     # Save working state
```

## Constraints from PROJECT.md
"""

        # Add constraints
        for constraint in spec.get("constraints", []):
            context += f"- {constraint}\n"

        # Write context file
        context_file = self.context_dir / "current.md"
        context_file.write_text(context)

        # Update memory
        self._update_memory(feature_id, validation)

    def _update_memory(self, feature_id: str, validation: Dict[str, Any]):
        """Update AI memory with current state"""
        memory_file = self.context_dir / "memory.json"

        # Load existing memory
        if memory_file.exists():
            memory = json.loads(memory_file.read_text())
        else:
            memory = {
                "features_completed": [],
                "common_errors": [],
                "working_patterns": [],
            }

        # Update with current session
        memory["current_feature"] = feature_id
        memory["last_validation"] = validation
        memory["session_started"] = self.current_session["started_at"]

        # Save memory
        memory_file.write_text(json.dumps(memory, indent=2))

    def store_context(self, key: str, value: Any):
        """Store context value for persistence"""
        conn = sqlite3.connect(self.rfd.db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO memory (key, value, updated_at)
            VALUES (?, ?, ?)
        """,
            (key, json.dumps(value), datetime.now().isoformat()),
        )
        conn.commit()

    def _get_stored_context(self, key: str) -> Optional[Any]:
        """Retrieve stored context value by key"""
        conn = sqlite3.connect(self.rfd.db_path)
        result = conn.execute(
            """
            SELECT value FROM memory WHERE key = ?
        """,
            (key,),
        ).fetchone()

        if result:
            return json.loads(result[0])
        return None

    def get_session_history(self) -> list:
        """Get history of all sessions"""
        conn = sqlite3.connect(self.rfd.db_path)
        sessions = conn.execute("""
            SELECT id, feature_id, started_at, ended_at, success
            FROM sessions
            ORDER BY started_at DESC
        """).fetchall()

        return [
            {
                "id": s[0],
                "feature_id": s[1],
                "started_at": s[2],
                "ended_at": s[3],
                "success": bool(s[4]),
            }
            for s in sessions
        ]
    
    def update_progress(self, checkpoint: str, status: str, data: Dict):
        """Update progress for current session"""
        if not self.current_session:
            return
        
        # Store progress in context
        progress_key = f"session_{self.current_session['id']}_progress"
        current_progress = self._get_stored_context(progress_key) or []
        current_progress.append({
            "checkpoint": checkpoint,
            "status": status,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        self.store_context(progress_key, current_progress)
    
    def get_context(self, key: Optional[str] = None) -> Any:
        """Get context - if no key, return current session context"""
        if key is None:
            # Return full context for current session
            if not self.current_session:
                return {}
            return {
                "session": self.current_session,
                "feature": self.get_current_feature(),
                "progress": self._get_stored_context(f"session_{self.current_session['id']}_progress")
            }
        
        # Original implementation with key
        conn = sqlite3.connect(self.rfd.db_path)
        result = conn.execute(
            """
            SELECT value FROM memory WHERE key = ?
        """,
            (key,),
        ).fetchone()

        if result:
            return json.loads(result[0])
        return None
    
    def get_recent_sessions(self, limit: int = 5) -> list:
        """Get recent sessions"""
        history = self.get_session_history()
        return history[:limit]
    
    def save_state(self, state: Dict):
        """Save session state"""
        if not self.current_session:
            return
        
        state_key = f"session_{self.current_session['id']}_state"
        self.store_context(state_key, state)
    
    def load_state(self) -> Optional[Dict]:
        """Load session state"""
        if not self.current_session:
            # Get most recent session
            history = self.get_session_history()
            if history:
                session_id = history[0]["id"]
                state_key = f"session_{session_id}_state"
                return self._get_stored_context(state_key)
        else:
            state_key = f"session_{self.current_session['id']}_state"
            return self._get_stored_context(state_key)
        return None
