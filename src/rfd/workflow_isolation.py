"""
Workflow Isolation Module
Adds git worktree isolation capabilities to existing SessionManager
"""

import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from .db_utils import get_db_connection


class WorkflowIsolation:
    """
    Add git worktree isolation to existing sessions without breaking compatibility
    """

    def __init__(self, rfd):
        self.rfd = rfd

    def create_isolated_worktree(self, feature_id: str, agent_type: str = "coding") -> Dict[str, Any]:
        """
        Create isolated git worktree for feature development
        Returns worktree info or None if creation fails
        """
        # Create worktree path
        worktree_path = Path(self.rfd.rfd_dir) / "worktrees" / f"{feature_id}-{agent_type}"
        branch_name = f"feature/{feature_id}-{agent_type}"

        # Ensure worktrees directory exists
        worktree_path.parent.mkdir(exist_ok=True)

        try:
            # Create git worktree
            result = subprocess.run(
                ["git", "worktree", "add", str(worktree_path), "-b", branch_name],
                cwd=str(self.rfd.rfd_dir.parent),
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Git worktree creation failed: {result.stderr}")

            # Record in database using existing git_worktrees table
            conn = get_db_connection(self.rfd.db_path)
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO git_worktrees (feature_id, worktree_path, branch_name, status)
                    VALUES (?, ?, ?, 'active')
                """,
                    (feature_id, str(worktree_path), branch_name),
                )

                worktree_id = cursor.lastrowid
                conn.commit()

                return {
                    "id": worktree_id,
                    "feature_id": feature_id,
                    "worktree_path": str(worktree_path),
                    "branch_name": branch_name,
                    "agent_type": agent_type,
                    "status": "active",
                }
            finally:
                conn.close()

        except Exception as e:
            # Clean up failed worktree if it was partially created
            if worktree_path.exists():
                subprocess.run(["git", "worktree", "remove", str(worktree_path)], capture_output=True)
            raise RuntimeError(f"Failed to create isolated worktree: {e}") from e

    def get_session_worktree(self, session_id: int) -> Optional[Dict[str, Any]]:
        """
        Get worktree info for a session (if it has one)
        """
        conn = get_db_connection(self.rfd.db_path)
        try:
            # Get session feature_id
            session = conn.execute("SELECT feature_id FROM sessions WHERE id = ?", (session_id,)).fetchone()

            if not session:
                return None

            feature_id = session[0]

            # Get active worktree for this feature
            worktree = conn.execute(
                """
                SELECT id, feature_id, worktree_path, branch_name, status
                FROM git_worktrees
                WHERE feature_id = ? AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            """,
                (feature_id,),
            ).fetchone()

            if worktree:
                return {
                    "id": worktree[0],
                    "feature_id": worktree[1],
                    "worktree_path": worktree[2],
                    "branch_name": worktree[3],
                    "status": worktree[4],
                }
            return None
        finally:
            conn.close()

    def cleanup_worktree(self, worktree_id: int) -> bool:
        """
        Clean up worktree when session ends
        """
        conn = get_db_connection(self.rfd.db_path)
        try:
            # Get worktree info
            worktree = conn.execute(
                "SELECT worktree_path, branch_name FROM git_worktrees WHERE id = ?", (worktree_id,)
            ).fetchone()

            if not worktree:
                return False

            worktree_path, branch_name = worktree

            # Remove git worktree
            result = subprocess.run(
                ["git", "worktree", "remove", worktree_path], cwd=str(self.rfd.rfd_dir.parent), capture_output=True
            )

            if result.returncode == 0:
                # Also delete the branch to prevent conflicts
                subprocess.run(
                    ["git", "branch", "-D", branch_name], cwd=str(self.rfd.rfd_dir.parent), capture_output=True
                )

                # Mark as cleaned up in database
                conn.execute(
                    """
                    UPDATE git_worktrees
                    SET status = 'cleaned_up', cleaned_up_at = datetime('now')
                    WHERE id = ?
                """,
                    (worktree_id,),
                )
                conn.commit()
                return True
            else:
                # Log error but don't fail - worktree might have been manually removed
                print(f"Warning: Could not remove worktree {worktree_path}: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error cleaning up worktree {worktree_id}: {e}")
            return False
        finally:
            conn.close()
