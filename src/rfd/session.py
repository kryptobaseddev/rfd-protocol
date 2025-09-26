"""
Session Manager for RFD
Manages development sessions and AI context
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional

from .db_utils import get_db_connection
from .workflow_isolation import WorkflowIsolation


class SessionManager:
    def __init__(self, rfd):
        # Handle both RFD objects and string paths for backwards compatibility
        if isinstance(rfd, str):
            # Create minimal RFD-like object for testing
            from pathlib import Path

            class MockRFD:
                def __init__(self, path_str):
                    self.rfd_dir = Path(path_str) / ".rfd"
                    self.rfd_dir.mkdir(exist_ok=True)
                    self.db_path = self.rfd_dir / "memory.db"
                    self._init_database()

                def load_project_spec(self):
                    return {"features": []}

                def _init_database(self):
                    """Initialize the database with required tables"""

                    conn = get_db_connection(self.db_path)
                    conn.executescript(
                        """
                        CREATE TABLE IF NOT EXISTS sessions (
                            id INTEGER PRIMARY KEY,
                            started_at TEXT,
                            ended_at TEXT,
                            feature_id TEXT,
                            success BOOLEAN
                        );

                        CREATE TABLE IF NOT EXISTS context (
                            id INTEGER PRIMARY KEY,
                            session_id INTEGER,
                            key TEXT,
                            value TEXT,
                            created_at TEXT,
                            FOREIGN KEY (session_id) REFERENCES sessions (id)
                        );

                        CREATE TABLE IF NOT EXISTS features (
                            id TEXT PRIMARY KEY,
                            description TEXT,
                            acceptance_criteria TEXT,
                            status TEXT DEFAULT 'pending',
                            created_at TEXT,
                            completed_at TEXT,
                            started_at TEXT,
                            assigned_to TEXT,
                            priority INTEGER DEFAULT 0,
                            tags JSON,
                            metadata JSON
                        );

                        CREATE TABLE IF NOT EXISTS checkpoints (
                            id INTEGER PRIMARY KEY,
                            feature_id TEXT,
                            timestamp TEXT,
                            validation_passed BOOLEAN,
                            build_passed BOOLEAN,
                            git_hash TEXT,
                            evidence JSON
                        );
                    """
                    )
                    conn.commit()
                    conn.close()

            self.rfd = MockRFD(rfd)
        else:
            self.rfd = rfd

        self.current_session = None
        self.context_dir = self.rfd.rfd_dir / "context"

        # Initialize workflow isolation capabilities
        self.isolation = WorkflowIsolation(self.rfd)

        # Load active session if exists
        self._load_active_session()

    def create_session(self, feature_id: str) -> int:
        """Create/start new development session - alias for start()"""
        return self.start(feature_id)

    def start(self, feature_id: str) -> int:
        """Start new development session"""
        # Check if feature exists in database (not markdown!)
        conn = get_db_connection(self.rfd.db_path)

        # First check if feature exists in database
        feature = conn.execute("SELECT id, description, status FROM features WHERE id = ?", (feature_id,)).fetchone()

        if not feature:
            # Get all available features from database for error message
            all_features = conn.execute("SELECT id FROM features ORDER BY created_at DESC").fetchall()
            available = [f[0] for f in all_features]

            conn.close()

            # Always raise error for undefined features
            if not available:
                raise ValueError(
                    f"Feature '{feature_id}' not found in database. No features exist yet - use 'rfd feature add' to create features."
                )
            else:
                raise ValueError(f"Feature '{feature_id}' not found in database. Available features: {available}")

        # End any existing session
        if self.current_session:
            self.end(success=False)

        # Create new session
        conn = get_db_connection(self.rfd.db_path)
        try:
            cursor = conn.execute(
                """
                INSERT INTO sessions (started_at, feature_id)
                VALUES (?, ?)
            """,
                (datetime.now().isoformat(), feature_id),
            )
            session_id = cursor.lastrowid
            conn.commit()
        finally:
            conn.close()

        self.current_session = {
            "id": session_id,
            "feature_id": feature_id,
            "feature": feature_id,  # Backward compatibility
            "started_at": datetime.now().isoformat(),
        }

        # Update feature status in database
        conn = get_db_connection(self.rfd.db_path)
        try:
            conn.execute(
                """
                UPDATE features SET status = 'building'
                WHERE id = ?
            """,
                (feature_id,),
            )
            conn.commit()
        finally:
            conn.close()

        # No longer update PROJECT.md - database is source of truth
        # Status already updated in database above

        # Generate context for AI using ContextManager
        from .context_manager import ContextManager

        context_mgr = ContextManager(self.rfd.rfd_dir)

        # Get feature data from database
        conn = get_db_connection(self.rfd.db_path)
        feature_data = conn.execute(
            "SELECT id, description, acceptance_criteria, status FROM features WHERE id = ?", (feature_id,)
        ).fetchone()
        conn.close()

        if feature_data:
            context_mgr.update_current_session(
                session_id=session_id,
                feature_id=feature_id,
                status="building",
                feature_data={"description": feature_data[1], "acceptance_criteria": feature_data[2]},
                validation_results=self.rfd.validator.validate(feature=feature_id),
            )

        return session_id

    def end(self, success: bool = True) -> Optional[int]:
        """End current session"""
        if not self.current_session:
            return None

        session_id = self.current_session["id"]

        # Create session snapshot before ending
        self._create_session_snapshot(session_id, success)

        # Update session record
        conn = get_db_connection(self.rfd.db_path)
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

            # Update PROJECT.md status
            from .project_updater import ProjectUpdater

            updater = ProjectUpdater(self.rfd)
            updater.update_feature_status(self.current_session["feature_id"], "complete")

        conn.commit()
        conn.close()

        self.current_session = None
        return session_id

    def get_current(self) -> Optional[Dict[str, Any]]:
        """Get current session info"""
        # If we have a session in memory, return it
        if self.current_session:
            return self.current_session

        # Otherwise, check database for any active sessions
        try:
            conn = get_db_connection(self.rfd.db_path)
            result = conn.execute(
                """
                SELECT id, started_at, feature_id
                FROM sessions
                WHERE ended_at IS NULL
                ORDER BY started_at DESC
                LIMIT 1
            """
            ).fetchone()
            conn.close()

            if result:
                session_id, started_at, feature_id = result
                # Load the session into memory
                self.current_session = {
                    "id": session_id,
                    "feature_id": feature_id,
                    "started_at": started_at,
                }
                return self.current_session
        except Exception:
            # If database doesn't exist or has issues, return None
            pass

        return None

    # Enhanced session methods with optional isolation
    def start_with_isolation(self, feature_id: str, agent_type: str = "coding") -> int:
        """
        Start session with git worktree isolation
        Creates isolated workspace for preventing context contamination
        """
        # First start normal session (all existing logic)
        session_id = self.start(feature_id)

        # Then add isolation
        try:
            worktree_info = self.isolation.create_isolated_worktree(feature_id, agent_type)

            # Update session in memory with worktree info
            if self.current_session:
                self.current_session["worktree"] = worktree_info
                self.current_session["isolated"] = True
                self.current_session["agent_type"] = agent_type

            return session_id
        except Exception as e:
            # If isolation fails, end the session to maintain consistency
            self.end(success=False)
            raise RuntimeError(f"Failed to create isolated session: {e}") from e

    def get_current_with_worktree(self) -> Optional[Dict[str, Any]]:
        """
        Get current session info including worktree details if isolated
        """
        current = self.get_current()
        if not current:
            return None

        # Check if session has associated worktree
        worktree_info = self.isolation.get_session_worktree(current["id"])
        if worktree_info:
            current["worktree"] = worktree_info
            current["isolated"] = True
            current["working_directory"] = worktree_info["worktree_path"]
        else:
            current["isolated"] = False
            current["working_directory"] = str(self.rfd.rfd_dir.parent)

        return current

    def end_with_cleanup(self, success: bool = True) -> Optional[int]:
        """
        End session with automatic worktree cleanup if isolated
        """
        if not self.current_session:
            return None

        # Check if session has worktree that needs cleanup
        worktree_info = self.isolation.get_session_worktree(self.current_session["id"])

        # End normal session first
        session_id = self.end(success)

        # Clean up worktree if it exists
        if worktree_info and success:
            # Only cleanup on success - preserve failed worktrees for debugging
            self.isolation.cleanup_worktree(worktree_info["id"])

        return session_id

    # Backwards compatible aliases
    def start_session(self, feature_id: str) -> int:
        """Alias for start() for backwards compatibility"""
        return self.start(feature_id)

    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """Alias for get_current() for backwards compatibility"""
        return self.get_current()

    def get_current_feature(self) -> Optional[str]:
        """Get current feature being worked on"""
        if self.current_session:
            return self.current_session["feature_id"]

        # Check for any in-progress features
        conn = get_db_connection(self.rfd.db_path)
        result = conn.execute(
            """
            SELECT id FROM features
            WHERE status = 'building'
            ORDER BY created_at DESC LIMIT 1
        """
        ).fetchone()

        return result[0] if result else None

    def suggest_next_action(self) -> str:
        """Suggest next action based on current state"""
        state = self.rfd.get_current_state()

        # Check validation status
        if not state["validation"]["passing"]:
            return "rfd validate  # Fix validation errors"

        # Check build status
        if not state["build"]["passing"]:
            return "rfd build  # Fix build errors"

        # Check for pending features
        conn = get_db_connection(self.rfd.db_path)
        pending = conn.execute(
            """
            SELECT id FROM features
            WHERE status = 'pending'
            ORDER BY created_at LIMIT 1
        """
        ).fetchone()

        if pending:
            return f"rfd session start {pending[0]}"

        return "rfd check  # All features complete!"

    def _generate_context(self, feature_id: str):
        """DEPRECATED - Now using ContextManager for context generation"""
        # This method is no longer used
        # Context is now generated by ContextManager in start() method
        pass

    def _update_memory(self, feature_id: str, validation: Dict[str, Any]):
        """DEPRECATED - Now using ContextManager for memory management"""
        # This method is no longer used
        # Memory is now managed by ContextManager
        pass

    def _create_session_snapshot(self, session_id: int, success: bool):
        """Create a snapshot of the current session state"""
        # Create snapshots directory (renamed from checkpoints)
        snapshot_dir = self.context_dir / "snapshots"
        snapshot_dir.mkdir(exist_ok=True)

        # Generate snapshot filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        feature_id = self.current_session.get("feature_id", "unknown")
        snapshot_file = snapshot_dir / f"session_{session_id}_{feature_id}_{timestamp}.json"

        # Gather all session data
        snapshot_data = {
            "session_id": session_id,
            "feature_id": feature_id,
            "started_at": self.current_session.get("started_at"),
            "ended_at": datetime.now().isoformat(),
            "success": success,
            "context": {},
            "memory": {},
            "validation": {},
            "checkpoints": [],
        }

        # Add current context
        context_file = self.context_dir / "current.md"
        if context_file.exists():
            snapshot_data["context"] = {
                "content": context_file.read_text(),
                "last_modified": datetime.fromtimestamp(context_file.stat().st_mtime).isoformat(),
            }

        # Add memory state
        memory_file = self.context_dir / "memory.json"
        if memory_file.exists():
            snapshot_data["memory"] = json.loads(memory_file.read_text())

        # Add validation results
        if hasattr(self.rfd, "validator"):
            validation = self.rfd.validator.validate(feature=feature_id)
            snapshot_data["validation"] = validation

        # Add checkpoints from this session
        conn = get_db_connection(self.rfd.db_path)
        checkpoints = conn.execute(
            """
            SELECT timestamp, validation_passed, build_passed, git_hash, evidence
            FROM checkpoints
            WHERE feature_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """,
            (feature_id,),
        ).fetchall()

        snapshot_data["checkpoints"] = [
            {
                "timestamp": cp[0],
                "validation_passed": bool(cp[1]),
                "build_passed": bool(cp[2]),
                "git_hash": cp[3],
                "evidence": json.loads(cp[4]) if cp[4] else {},
            }
            for cp in checkpoints
        ]

        # Save snapshot
        snapshot_file.write_text(json.dumps(snapshot_data, indent=2))

        # Also migrate old checkpoints directory if it exists
        old_checkpoint_dir = self.context_dir / "checkpoints"
        if old_checkpoint_dir.exists() and old_checkpoint_dir.is_dir():
            # Rename to snapshots if empty
            if not list(old_checkpoint_dir.iterdir()):
                old_checkpoint_dir.rmdir()
            else:
                # Move any existing files
                import shutil

                for old_file in old_checkpoint_dir.iterdir():
                    if old_file.is_file():
                        shutil.move(str(old_file), str(snapshot_dir / old_file.name))

    def store_context(self, key: str, value: Any):
        """Store context value for persistence"""
        conn = get_db_connection(self.rfd.db_path)
        conn.execute(
            """
            INSERT OR REPLACE INTO memory (key, value, updated_at)
            VALUES (?, ?, ?)
        """,
            (key, json.dumps(value), datetime.now().isoformat()),
        )
        conn.commit()

    def get_context(self, key: Optional[str] = None) -> Optional[Any]:
        """Retrieve stored context value or full context if no key"""
        if key is None:
            # Return full context for current session
            if not self.current_session:
                return {}
            return {
                "session": self.current_session,
                "feature": self.get_current_feature(),
            }

        # Original implementation with key
        conn = get_db_connection(self.rfd.db_path)
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
        conn = get_db_connection(self.rfd.db_path)
        sessions = conn.execute(
            """
            SELECT id, feature_id, started_at, ended_at, success
            FROM sessions
            ORDER BY started_at DESC
        """
        ).fetchall()

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

    def _load_active_session(self):
        """Load active session on initialization"""
        conn = get_db_connection(self.rfd.db_path)

        # Find active session (started but not ended)
        result = conn.execute(
            """
            SELECT id, feature_id, started_at
            FROM sessions
            WHERE ended_at IS NULL
            ORDER BY started_at DESC
            LIMIT 1
            """
        ).fetchone()

        if result:
            self.current_session = {
                "id": result[0],
                "feature_id": result[1],
                "started_at": result[2],
            }

        conn.close()
