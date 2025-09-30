"""
Real-time workflow enforcement with actual database integration
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .db_utils import get_db_connection
from .rfd import RFD


class WorkflowEnforcer:
    """
    Real enforcement that actually prevents spec violations
    """

    def __init__(self, rfd: Optional[RFD] = None):
        self.rfd = rfd or RFD()
        self._ensure_tables()

    def _ensure_tables(self):
        """Create enforcement tables if they don't exist"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            # Violations table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    feature_id TEXT,
                    violation_type TEXT,
                    description TEXT,
                    file_path TEXT,
                    prevented BOOLEAN DEFAULT 0
                )
            """
            )

            # Enforcement status
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS enforcement_status (
                    feature_id TEXT PRIMARY KEY,
                    active BOOLEAN DEFAULT 0,
                    started_at TEXT,
                    scope_baseline TEXT
                )
            """
            )

            conn.commit()
        finally:
            conn.close()

    def start_enforcement(self, feature_id: str) -> Dict[str, Any]:
        """Start enforcement for a feature"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            # Check if feature exists
            feature = conn.execute("SELECT id FROM features WHERE id = ?", (feature_id,)).fetchone()

            if not feature:
                return {"status": "error", "message": f"Feature {feature_id} not found"}

            # Capture baseline
            baseline = self._capture_baseline()

            # Store enforcement status
            conn.execute(
                """
                INSERT OR REPLACE INTO enforcement_status
                (feature_id, active, started_at, scope_baseline)
                VALUES (?, 1, datetime('now'), ?)
            """,
                (feature_id, json.dumps(baseline)),
            )

            conn.commit()

            return {"status": "active", "feature": feature_id, "baseline": baseline}
        finally:
            conn.close()

    def stop_enforcement(self, feature_id: str) -> Dict[str, Any]:
        """Stop enforcement"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            conn.execute("UPDATE enforcement_status SET active = 0 WHERE feature_id = ?", (feature_id,))
            conn.commit()
            return {"status": "stopped", "feature": feature_id}
        finally:
            conn.close()

    def validate_change(self, file_path: str, feature_id: str) -> Dict[str, Any]:
        """Validate a file change against specs"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            # Check enforcement status
            status = conn.execute(
                "SELECT active, scope_baseline FROM enforcement_status WHERE feature_id = ?", (feature_id,)
            ).fetchone()

            if not status or not status[0]:
                return {"allowed": True, "reason": "Enforcement not active"}

            # Check if file is in scope
            baseline = json.loads(status[1]) if status[1] else {}
            allowed_paths = baseline.get("paths", [])

            file_p = Path(file_path)
            in_scope = any(file_p.match(pattern) or str(file_p).startswith(pattern) for pattern in allowed_paths)

            if not in_scope:
                # Log violation
                conn.execute(
                    """
                    INSERT INTO violations
                    (feature_id, violation_type, description, file_path, prevented)
                    VALUES (?, 'out_of_scope', ?, ?, 1)
                """,
                    (feature_id, f"File {file_path} not in feature scope", file_path),
                )
                conn.commit()

                return {"allowed": False, "reason": f"File {file_path} is out of scope for feature {feature_id}"}

            return {"allowed": True, "reason": "Change within scope"}
        finally:
            conn.close()

    def _capture_baseline(self) -> Dict[str, Any]:
        """Capture current state as baseline"""
        # Get current files
        src_files = list(Path("src").glob("**/*.py")) if Path("src").exists() else []
        test_files = list(Path("tests").glob("**/*.py")) if Path("tests").exists() else []

        return {
            "paths": ["src/", "tests/", ".rfd/"],
            "file_count": len(src_files) + len(test_files),
            "timestamp": datetime.now().isoformat(),
        }


class ScopeDriftDetector:
    """
    Detect when work drifts from original scope
    """

    def __init__(self, rfd: Optional[RFD] = None):
        self.rfd = rfd or RFD()
        self.enforcer = WorkflowEnforcer(rfd)

    def detect_drift(self, feature_id: str) -> Dict[str, Any]:
        """Check if current work has drifted from scope"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            # Get baseline
            status = conn.execute(
                "SELECT scope_baseline FROM enforcement_status WHERE feature_id = ?", (feature_id,)
            ).fetchone()

            if not status or not status[0]:
                return {"drift_detected": False, "reason": "No baseline found"}

            baseline = json.loads(status[0])
            current = self.enforcer._capture_baseline()

            # Simple drift detection - file count increased significantly
            original_count = baseline.get("file_count", 0)
            current_count = current.get("file_count", 0)

            if current_count > original_count * 1.3:  # 30% increase
                return {
                    "drift_detected": True,
                    "reason": f"File count increased from {original_count} to {current_count}",
                    "recommendation": "Review new files to ensure they're in scope",
                }

            return {
                "drift_detected": False,
                "metrics": {"original_files": original_count, "current_files": current_count},
            }
        finally:
            conn.close()


class MultiAgentCoordinator:
    """
    Coordinate multiple agents with database persistence
    """

    def __init__(self, rfd: Optional[RFD] = None):
        self.rfd = rfd or RFD()
        self._ensure_tables()

    def _ensure_tables(self):
        """Create agent coordination tables"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            # Drop old table if it exists with wrong schema
            cursor = conn.execute("SELECT sql FROM sqlite_master WHERE name='agent_handoffs'")
            existing = cursor.fetchone()
            if existing and "from_agent TEXT" not in existing[0]:
                conn.execute("DROP TABLE agent_handoffs")

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    capabilities TEXT,
                    status TEXT DEFAULT 'idle',
                    registered_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_handoffs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_agent TEXT,
                    to_agent TEXT,
                    task_description TEXT,
                    context TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed_at TEXT
                )
            """
            )

            conn.commit()
        finally:
            conn.close()

    def register_agent(self, agent_id: str, capabilities: List[str]) -> Dict[str, Any]:
        """Register an agent"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO agents (agent_id, capabilities, status)
                VALUES (?, ?, 'idle')
            """,
                (agent_id, json.dumps(capabilities)),
            )
            conn.commit()

            return {"status": "registered", "agent_id": agent_id}
        finally:
            conn.close()

    def create_handoff(self, from_agent: str, to_agent: str, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create handoff between agents"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            cursor = conn.execute(
                """
                INSERT INTO agent_handoffs
                (from_agent, to_agent, task_description, context)
                VALUES (?, ?, ?, ?)
            """,
                (from_agent, to_agent, task, json.dumps(context)),
            )

            conn.commit()

            return {"status": "created", "handoff_id": cursor.lastrowid, "from": from_agent, "to": to_agent}
        finally:
            conn.close()

    def get_pending_handoffs(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get pending handoffs for an agent"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            handoffs = conn.execute(
                """
                SELECT id, from_agent, task_description, context, created_at
                FROM agent_handoffs
                WHERE to_agent = ? AND status = 'pending'
                ORDER BY created_at
            """,
                (agent_id,),
            ).fetchall()

            return [
                {"id": h[0], "from": h[1], "task": h[2], "context": json.loads(h[3]) if h[3] else {}, "created": h[4]}
                for h in handoffs
            ]
        finally:
            conn.close()

    def trigger_review(self, trigger_type: str, feature_id: str) -> Dict[str, Any]:
        """
        Trigger automated review based on event type

        Args:
            trigger_type: 'pre_commit' or 'post_build'
            feature_id: Feature being reviewed

        Returns:
            Review results with pass/fail status
        """
        from .validation import ValidationEngine
        from .build import BuildEngine

        conn = get_db_connection(self.rfd.db_path)
        try:
            # Record review trigger
            cursor = conn.execute(
                """
                INSERT INTO qa_cycles (feature_id, cycle_number, status, started_at)
                SELECT ?, COALESCE(MAX(cycle_number), 0) + 1, 'reviewing', datetime('now')
                FROM qa_cycles WHERE feature_id = ?
            """,
                (feature_id, feature_id),
            )
            cycle_id = cursor.lastrowid
            conn.commit()

            results = {"cycle_id": cycle_id, "trigger": trigger_type, "passed": True, "issues": [], "suggestions": []}

            # Run appropriate review based on trigger
            if trigger_type == "pre_commit":
                # Check for mock data
                validator = ValidationEngine(self.rfd)
                validation_results = validator.validate(feature=feature_id)

                if not validation_results["passing"]:
                    results["passed"] = False
                    results["issues"].append("Validation failed")
                    for result in validation_results.get("results", []):
                        if not result["passed"]:
                            results["issues"].append(result["message"])

            elif trigger_type == "post_build":
                # Check build status
                builder = BuildEngine(self.rfd)
                if not builder.run_tests():
                    results["passed"] = False
                    results["issues"].append("Tests failed")
                    results["suggestions"].append("Fix failing tests before proceeding")

            # Record review results
            conn.execute(
                """
                INSERT INTO review_results (cycle_id, review_type, passed, issues, suggestions)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    cycle_id,
                    trigger_type,
                    results["passed"],
                    json.dumps(results["issues"]),
                    json.dumps(results["suggestions"]),
                ),
            )

            # Update cycle status
            status = "passed" if results["passed"] else "failed"
            conn.execute(
                """
                UPDATE qa_cycles 
                SET status = ?, completed_at = datetime('now')
                WHERE id = ?
            """,
                (status, cycle_id),
            )

            conn.commit()
            return results

        finally:
            conn.close()

    def get_review_status(self, feature_id: str) -> Dict[str, Any]:
        """Get current review status for a feature"""
        conn = get_db_connection(self.rfd.db_path)
        try:
            cycle = conn.execute(
                """
                SELECT id, cycle_number, status, started_at, completed_at
                FROM qa_cycles
                WHERE feature_id = ?
                ORDER BY cycle_number DESC
                LIMIT 1
            """,
                (feature_id,),
            ).fetchone()

            if not cycle:
                return {"status": "no_reviews", "cycles": 0}

            results = conn.execute(
                """
                SELECT review_type, passed, issues, suggestions
                FROM review_results
                WHERE cycle_id = ?
            """,
                (cycle[0],),
            ).fetchall()

            return {
                "status": cycle[2],
                "cycle_number": cycle[1],
                "started": cycle[3],
                "completed": cycle[4],
                "reviews": [
                    {
                        "type": r[0],
                        "passed": bool(r[1]),
                        "issues": json.loads(r[2]) if r[2] else [],
                        "suggestions": json.loads(r[3]) if r[3] else [],
                    }
                    for r in results
                ],
            }
        finally:
            conn.close()


# Alias for backwards compatibility and testing
EnforcementEngine = MultiAgentCoordinator
