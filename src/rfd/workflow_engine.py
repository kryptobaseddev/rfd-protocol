"""
Workflow Engine: Query-Driven Gated Linear Flow
Enforces progression through checkpoints with validation gates
"""

import sqlite3
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class WorkflowState(Enum):
    """Workflow states with strict progression"""

    IDEATION = "ideation"
    SPECIFICATION = "specification"
    CLARIFICATION = "clarification"
    PLANNING = "planning"
    TASK_GENERATION = "task_generation"
    IMPLEMENTATION = "implementation"
    VALIDATION = "validation"
    COMPLETION = "completion"


class GatedWorkflow:
    """
    Enforces linear progression through development phases
    Each gate requires validation before proceeding
    """

    def __init__(self, rfd):
        self.rfd = rfd
        self.db_path = rfd.db_path
        self._init_workflow_tables()

        # Define the linear flow with gates
        self.flow = [
            WorkflowState.IDEATION,
            WorkflowState.SPECIFICATION,
            WorkflowState.CLARIFICATION,
            WorkflowState.PLANNING,
            WorkflowState.TASK_GENERATION,
            WorkflowState.IMPLEMENTATION,
            WorkflowState.VALIDATION,
            WorkflowState.COMPLETION,
        ]

        # Define gate requirements for each state
        self.gates = {
            WorkflowState.IDEATION: self._validate_ideation,
            WorkflowState.SPECIFICATION: self._validate_specification,
            WorkflowState.CLARIFICATION: self._validate_clarification,
            WorkflowState.PLANNING: self._validate_planning,
            WorkflowState.TASK_GENERATION: self._validate_tasks,
            WorkflowState.IMPLEMENTATION: self._validate_implementation,
            WorkflowState.VALIDATION: self._validate_validation,
            WorkflowState.COMPLETION: self._validate_completion,
        }

    def _init_workflow_tables(self):
        """Create workflow tracking tables"""
        conn = sqlite3.connect(self.db_path)

        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS workflow_state (
                feature_id TEXT PRIMARY KEY,
                current_state TEXT NOT NULL,
                locked_by TEXT,  -- Session/user that has lock
                locked_at TEXT,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS workflow_checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_id TEXT NOT NULL,
                state TEXT NOT NULL,
                passed BOOLEAN DEFAULT 0,
                validation_data JSON,
                timestamp TEXT,
                FOREIGN KEY (feature_id) REFERENCES features(id)
            );

            CREATE TABLE IF NOT EXISTS workflow_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_id TEXT NOT NULL,
                state TEXT NOT NULL,
                query TEXT NOT NULL,
                answer TEXT,
                resolved BOOLEAN DEFAULT 0,
                timestamp TEXT,
                FOREIGN KEY (feature_id) REFERENCES features(id)
            );

            CREATE TABLE IF NOT EXISTS drift_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_id TEXT,
                session_id TEXT,
                attempted_action TEXT,
                blocked_reason TEXT,
                timestamp TEXT
            );

            CREATE TABLE IF NOT EXISTS hallucination_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                claim_type TEXT,
                claim TEXT,
                reason TEXT
            );
        """
        )

        conn.commit()
        conn.close()

    def start_feature(self, feature_id: str, session_id: str) -> Tuple[bool, str]:
        """
        Start or resume a feature with session locking
        Returns (success, message)
        """
        conn = sqlite3.connect(self.db_path)

        # Check if feature exists
        feature = conn.execute("SELECT id FROM features WHERE id = ?", (feature_id,)).fetchone()

        if not feature:
            conn.close()
            return False, f"Feature {feature_id} not found in database"

        # Check for existing workflow state
        state = conn.execute(
            "SELECT current_state, locked_by, locked_at FROM workflow_state WHERE feature_id = ?",
            (feature_id,),
        ).fetchone()

        if state:
            current_state, locked_by, locked_at = state

            # Check if locked by another session
            if locked_by and locked_by != session_id:
                # Check if lock is stale (> 30 minutes)
                if locked_at:
                    from datetime import timedelta

                    lock_time = datetime.fromisoformat(locked_at)
                    if datetime.now() - lock_time > timedelta(minutes=30):
                        # Stale lock, steal it
                        conn.execute(
                            "UPDATE workflow_state SET locked_by = ?, locked_at = ? WHERE feature_id = ?",
                            (session_id, datetime.now().isoformat(), feature_id),
                        )
                    else:
                        conn.close()
                        return (
                            False,
                            f"Feature locked by session {locked_by} at {locked_at}",
                        )

            # Update lock
            conn.execute(
                "UPDATE workflow_state SET locked_by = ?, locked_at = ?, updated_at = ? WHERE feature_id = ?",
                (
                    session_id,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    feature_id,
                ),
            )
        else:
            # Create new workflow state
            conn.execute(
                """INSERT INTO workflow_state
                   (feature_id, current_state, locked_by, locked_at, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    feature_id,
                    WorkflowState.IDEATION.value,
                    session_id,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                ),
            )
            current_state = WorkflowState.IDEATION.value

        conn.commit()
        conn.close()

        return True, f"Feature {feature_id} started at state: {current_state}"

    def get_current_state(self, feature_id: str) -> Optional[WorkflowState]:
        """Get current workflow state for a feature"""
        conn = sqlite3.connect(self.db_path)
        result = conn.execute(
            "SELECT current_state FROM workflow_state WHERE feature_id = ?",
            (feature_id,),
        ).fetchone()
        conn.close()

        if result:
            return WorkflowState(result[0])
        return None

    def can_proceed(self, feature_id: str) -> Tuple[bool, str]:
        """
        Check if current state gate is satisfied and we can proceed
        Returns (can_proceed, reason)
        """
        current = self.get_current_state(feature_id)
        if not current:
            return False, "No workflow state found"

        # Run gate validation for current state
        gate_func = self.gates.get(current)
        if gate_func:
            passed, reason = gate_func(feature_id)
            if not passed:
                return False, f"Gate not satisfied: {reason}"

        return True, "Ready to proceed"

    def proceed_to_next(self, feature_id: str, session_id: str) -> Tuple[bool, str]:
        """
        Attempt to move to next state if gate is satisfied
        Returns (success, message)
        """
        # Check lock
        conn = sqlite3.connect(self.db_path)
        lock = conn.execute("SELECT locked_by FROM workflow_state WHERE feature_id = ?", (feature_id,)).fetchone()

        if not lock or lock[0] != session_id:
            conn.close()
            return False, "Feature not locked by this session"

        # Check if can proceed
        can_go, reason = self.can_proceed(feature_id)
        if not can_go:
            # Log drift attempt
            conn.execute(
                """INSERT INTO drift_log (feature_id, session_id, attempted_action, blocked_reason, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    feature_id,
                    session_id,
                    "proceed_to_next",
                    reason,
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            conn.close()
            return False, reason

        # Get current state and find next
        current = self.get_current_state(feature_id)
        current_index = self.flow.index(current)

        if current_index >= len(self.flow) - 1:
            conn.close()
            return False, "Already at final state"

        next_state = self.flow[current_index + 1]

        # Record checkpoint
        conn.execute(
            """INSERT INTO workflow_checkpoints (feature_id, state, passed, timestamp)
               VALUES (?, ?, ?, ?)""",
            (feature_id, current.value, True, datetime.now().isoformat()),
        )

        # Update state
        conn.execute(
            "UPDATE workflow_state SET current_state = ?, updated_at = ? WHERE feature_id = ?",
            (next_state.value, datetime.now().isoformat(), feature_id),
        )

        conn.commit()
        conn.close()

        return True, f"Progressed to {next_state.value}"

    def add_query(self, feature_id: str, query: str) -> int:
        """
        Add a query that needs resolution before proceeding
        Returns query ID
        """
        conn = sqlite3.connect(self.db_path)
        current = self.get_current_state(feature_id)

        cursor = conn.execute(
            """INSERT INTO workflow_queries (feature_id, state, query, timestamp)
               VALUES (?, ?, ?, ?)""",
            (
                feature_id,
                current.value if current else None,
                query,
                datetime.now().isoformat(),
            ),
        )

        query_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return query_id

    def resolve_query(self, query_id: int, answer: str):
        """Resolve a query with an answer"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE workflow_queries SET answer = ?, resolved = 1 WHERE id = ?",
            (answer, query_id),
        )
        conn.commit()
        conn.close()

    def get_unresolved_queries(self, feature_id: str) -> List[Dict]:
        """Get all unresolved queries for a feature"""
        conn = sqlite3.connect(self.db_path)
        queries = conn.execute(
            """SELECT id, query, state, timestamp
               FROM workflow_queries
               WHERE feature_id = ? AND resolved = 0
               ORDER BY timestamp""",
            (feature_id,),
        ).fetchall()
        conn.close()

        return [{"id": q[0], "query": q[1], "state": q[2], "timestamp": q[3]} for q in queries]

    def block_drift(self, feature_id: str, action: str) -> bool:
        """
        Block an action that would cause drift
        Returns True if blocked
        """
        current = self.get_current_state(feature_id)

        # List of actions that would cause drift
        drift_actions = [
            "start_new_feature",
            "switch_context",
            "skip_validation",
            "mock_data",
            "incomplete_implementation",
        ]

        if action in drift_actions:
            conn = sqlite3.connect(self.db_path)
            conn.execute(
                """INSERT INTO drift_log (feature_id, session_id, attempted_action, blocked_reason, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    feature_id,
                    "current",
                    action,
                    f"Action would cause drift from {current.value}",
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
            conn.close()
            return True

        return False

    # Gate validation functions

    def _validate_ideation(self, feature_id: str) -> Tuple[bool, str]:
        """Validate ideation phase is complete"""
        # Check if feature has description and acceptance criteria
        spec = self.rfd.load_project_spec()
        for feature in spec.get("features", []):
            if feature["id"] == feature_id:
                if feature.get("description") and feature.get("acceptance"):
                    return True, "Ideation complete"
                return False, "Feature needs description and acceptance criteria"
        return False, "Feature not found in spec"

    def _validate_specification(self, feature_id: str) -> Tuple[bool, str]:
        """Validate specification is complete"""
        # Check if spec file exists
        if list(Path("specs").glob(f"*-{feature_id}/spec.md")):
            return True, "Specification exists"
        return False, "Specification file not created"

    def _validate_clarification(self, feature_id: str) -> Tuple[bool, str]:
        """Validate all queries are resolved"""
        queries = self.get_unresolved_queries(feature_id)
        if queries:
            return False, f"{len(queries)} unresolved queries"
        return True, "All queries resolved"

    def _validate_planning(self, feature_id: str) -> Tuple[bool, str]:
        """Validate plan is complete"""
        if list(Path("specs").glob(f"*-{feature_id}/plan.md")):
            return True, "Plan exists"
        return False, "Plan file not created"

    def _validate_tasks(self, feature_id: str) -> Tuple[bool, str]:
        """Validate tasks are generated"""
        conn = sqlite3.connect(self.db_path)
        tasks = conn.execute("SELECT COUNT(*) FROM tasks WHERE feature_id = ?", (feature_id,)).fetchone()
        conn.close()

        if tasks and tasks[0] > 0:
            return True, f"{tasks[0]} tasks generated"
        return False, "No tasks generated"

    def _validate_implementation(self, feature_id: str) -> Tuple[bool, str]:
        """Validate implementation progress"""
        # Check if any code files exist for the feature
        # This is where AI hallucination detection happens
        from .ai_validator import AIClaimValidator

        validator = AIClaimValidator()

        # Check for common implementation claims
        test_claims = [
            f"Created src/{feature_id}/__init__.py",
            f"Implemented {feature_id} functionality",
            f"Added tests for {feature_id}",
        ]

        for claim in test_claims:
            passed, _ = validator.validate_ai_claims(claim)
            if passed:
                return True, "Implementation detected"

        return False, "No implementation found"

    def _validate_validation(self, feature_id: str) -> Tuple[bool, str]:
        """Validate that validation passed"""
        # Run actual validation
        validation_result = self.rfd.validator.validate(feature=feature_id)

        if validation_result["passing"]:
            return True, "Validation passed"

        failed_count = sum(1 for r in validation_result["results"] if not r["passed"])
        return False, f"{failed_count} validation failures"

    def _validate_completion(self, feature_id: str) -> Tuple[bool, str]:
        """Validate feature is truly complete"""
        # Check all previous gates
        for state in self.flow[:-1]:
            gate_func = self.gates.get(state)
            if gate_func:
                passed, reason = gate_func(feature_id)
                if not passed:
                    return False, f"Incomplete: {state.value} - {reason}"

        return True, "Feature complete"

    def get_workflow_status(self, feature_id: str) -> Dict[str, Any]:
        """Get complete workflow status for a feature"""
        current = self.get_current_state(feature_id)
        if not current:
            return {"error": "No workflow found"}

        conn = sqlite3.connect(self.db_path)

        # Get checkpoints
        checkpoints = conn.execute(
            """SELECT state, passed, timestamp
               FROM workflow_checkpoints
               WHERE feature_id = ?
               ORDER BY timestamp""",
            (feature_id,),
        ).fetchall()

        # Get drift attempts
        drift_attempts = conn.execute(
            """SELECT COUNT(*) FROM drift_log WHERE feature_id = ?""", (feature_id,)
        ).fetchone()[0]

        # Get hallucination attempts
        hallucinations = conn.execute("SELECT COUNT(*) FROM hallucination_log").fetchone()[0]

        conn.close()

        # Build status
        status = {
            "feature_id": feature_id,
            "current_state": current.value,
            "progress": f"{self.flow.index(current) + 1}/{len(self.flow)}",
            "checkpoints_passed": [{"state": c[0], "passed": c[1], "timestamp": c[2]} for c in checkpoints],
            "drift_attempts_blocked": drift_attempts,
            "hallucinations_caught": hallucinations,
            "can_proceed": self.can_proceed(feature_id),
            "unresolved_queries": len(self.get_unresolved_queries(feature_id)),
        }

        return status

    def enforce_linear_flow(self, feature_id: str, requested_action: str) -> Tuple[bool, str]:
        """
        Main enforcement point - validates any action against current state
        Returns (allowed, reason)
        """
        current = self.get_current_state(feature_id)

        if not current:
            return False, "No workflow initialized"

        # Map actions to required states
        action_requirements = {
            "create_spec": WorkflowState.SPECIFICATION,
            "add_clarification": WorkflowState.CLARIFICATION,
            "create_plan": WorkflowState.PLANNING,
            "generate_tasks": WorkflowState.TASK_GENERATION,
            "implement": WorkflowState.IMPLEMENTATION,
            "validate": WorkflowState.VALIDATION,
            "complete": WorkflowState.COMPLETION,
        }

        required_state = action_requirements.get(requested_action)

        if required_state:
            if current != required_state:
                return (
                    False,
                    f"Action '{requested_action}' requires state {required_state.value}, currently in {current.value}",
                )

        return True, "Action allowed"
