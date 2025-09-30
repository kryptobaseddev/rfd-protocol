"""
Automatic Session Handoff System
No manual documents - everything from database and code
"""

import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from typing import Any, Dict, List


class AutoHandoff:
    """
    Programmatic session handoff - no manual documents
    Everything computed from system state
    """

    def __init__(self, rfd):
        self.rfd = rfd
        self.db_path = rfd.db_path

    def generate_handoff(self) -> Dict[str, Any]:
        """
        Generate complete handoff data programmatically
        This replaces ALL manual documentation
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": self._get_system_status(),
            "current_session": self._get_current_session(),
            "workflow_state": self._get_workflow_state(),
            "pending_work": self._get_pending_work(),
            "validation_status": self._get_validation_status(),
            "available_commands": self._get_available_commands(),
            "next_actions": self._get_next_actions(),
            "blockers": self._get_blockers(),
            "system_health": self._run_health_checks(),
        }

    def _get_system_status(self) -> Dict[str, Any]:
        """Get overall system status from database"""
        conn = sqlite3.connect(self.db_path)

        # Count features by status
        features = conn.execute(
            """
            SELECT status, COUNT(*) FROM features GROUP BY status
        """
        ).fetchall()

        feature_counts = dict(features)

        # Get module count
        module_count = len(list(Path("src/rfd").glob("*.py")))

        # Check for hallucination detection
        hallucination_count = (
            conn.execute("SELECT COUNT(*) FROM hallucination_log").fetchone()[0]
            if self._table_exists("hallucination_log")
            else 0
        )

        # Check drift attempts
        drift_count = (
            conn.execute("SELECT COUNT(*) FROM drift_log").fetchone()[0] if self._table_exists("drift_log") else 0
        )

        conn.close()

        return {
            "modules_available": module_count,
            "features": feature_counts,
            "total_features": sum(feature_counts.values()),
            "completion_percentage": (
                feature_counts.get("complete", 0) / sum(feature_counts.values()) * 100 if feature_counts else 0
            ),
            "hallucinations_caught": hallucination_count,
            "drift_attempts_blocked": drift_count,
            "database_healthy": True,
        }

    def _get_current_session(self) -> Dict[str, Any]:
        """Get current session info from context files and DB"""
        current_file = self.rfd.rfd_dir / "context" / "current.md"
        memory_file = self.rfd.rfd_dir / "context" / "memory.json"

        session_info = {}

        # Parse current.md for session data
        if current_file.exists():
            import frontmatter

            with open(current_file) as f:
                content = frontmatter.load(f)
                if content.metadata:
                    session_info["feature"] = content.metadata.get("feature")
                    session_info["started"] = content.metadata.get("started")
                    session_info["status"] = content.metadata.get("status")

        # Load memory
        if memory_file.exists():
            memory = json.loads(memory_file.read_text())
            session_info["memory"] = {
                "current_feature": memory.get("current_feature"),
                "last_action": memory.get("last_action"),
                "session_started": memory.get("session_started"),
            }

        # Get active sessions from DB
        conn = sqlite3.connect(self.db_path)
        active_session = conn.execute(
            """
            SELECT id, feature_id, started_at
            FROM sessions
            WHERE ended_at IS NULL
            ORDER BY started_at DESC
            LIMIT 1
        """
        ).fetchone()

        if active_session:
            session_info["session_id"] = active_session[0]
            session_info["feature_id"] = active_session[1]
            session_info["started_at"] = active_session[2]

        conn.close()

        return session_info

    def _get_workflow_state(self) -> Dict[str, Any]:
        """Get workflow state for all features"""
        if not self._table_exists("workflow_state"):
            return {"error": "Workflow not initialized"}

        conn = sqlite3.connect(self.db_path)

        workflows = conn.execute(
            """
            SELECT feature_id, current_state, locked_by, locked_at
            FROM workflow_state
            ORDER BY updated_at DESC
        """
        ).fetchall()

        conn.close()

        return {
            "active_workflows": [
                {"feature": w[0], "state": w[1], "locked_by": w[2], "locked_at": w[3]} for w in workflows
            ]
        }

    def _get_pending_work(self) -> Dict[str, Any]:
        """Get all pending work items"""
        conn = sqlite3.connect(self.db_path)

        # Pending features
        pending_features = conn.execute(
            """
            SELECT id, description FROM features WHERE status = 'pending'
        """
        ).fetchall()

        # Pending tasks
        pending_tasks = (
            conn.execute(
                """
            SELECT feature_id, description FROM tasks WHERE status = 'pending'
        """
            ).fetchall()
            if self._table_exists("tasks")
            else []
        )

        # Unresolved queries
        unresolved_queries = (
            conn.execute(
                """
            SELECT id, feature_id, query FROM workflow_queries WHERE resolved = 0
        """
            ).fetchall()
            if self._table_exists("workflow_queries")
            else []
        )

        conn.close()

        return {
            "pending_features": [{"id": f[0], "description": f[1]} for f in pending_features],
            "pending_tasks": [{"feature": t[0], "description": t[1]} for t in pending_tasks],
            "unresolved_queries": [{"id": q[0], "feature": q[1], "query": q[2]} for q in unresolved_queries],
        }

    def _get_validation_status(self) -> Dict[str, Any]:
        """Get validation status"""
        # Run actual validation
        validation_result = self.rfd.validator.validate()
        build_status = self.rfd.builder.get_status()

        return {
            "validation_passing": validation_result["passing"],
            "validation_failures": [r for r in validation_result.get("results", []) if not r["passed"]],
            "build_passing": build_status["passing"],
            "build_message": build_status.get("message", ""),
        }

    def _get_available_commands(self) -> List[str]:
        """Get list of available RFD commands"""
        try:
            result = subprocess.run(["rfd", "--help"], capture_output=True, text=True, timeout=2)

            # Parse commands from help output
            commands = []
            in_commands = False
            for line in result.stdout.split("\n"):
                if "Commands:" in line:
                    in_commands = True
                    continue
                if in_commands and line.strip() and not line.startswith(" "):
                    break
                if in_commands and line.strip():
                    cmd = line.split()[0]
                    commands.append(f"rfd {cmd}")

            return commands
        except Exception:
            return ["rfd --help"]

    def _get_next_actions(self) -> List[str]:
        """Determine next actions based on current state"""
        actions = []

        # Get current session
        session = self._get_current_session()

        if not session.get("feature"):
            actions.append("rfd session start <feature>")
            actions.append("rfd workflow start <feature>")
            return actions

        feature = session.get("feature")

        # Check workflow state
        workflow = self._get_workflow_state()
        if workflow and workflow.get("active_workflows"):
            current_workflow = workflow["active_workflows"][0]
            state = current_workflow.get("state")

            # Map states to actions
            state_actions = {
                "ideation": "rfd workflow proceed",
                "specification": f"rfd speckit specify {feature}",
                "clarification": "rfd workflow proceed",
                "planning": f"rfd speckit plan {feature}",
                "task_generation": f"rfd speckit tasks {feature}",
                "implementation": f"rfd speckit implement {feature}",
                "validation": f"rfd validate --feature {feature}",
                "completion": f"rfd complete {feature}",
            }

            if state in state_actions:
                actions.append(state_actions[state])

        # Check validation
        validation = self._get_validation_status()
        if not validation["validation_passing"]:
            actions.append("rfd validate")
        if not validation["build_passing"]:
            actions.append("rfd build")

        # Default actions
        if not actions:
            actions.extend(
                [
                    "rfd check",
                    "rfd status",
                    "rfd workflow status " + feature if feature else "",
                ]
            )

        return actions

    def _get_blockers(self) -> List[Dict[str, str]]:
        """Identify current blockers"""
        blockers = []

        # Check for unresolved queries
        pending = self._get_pending_work()
        if pending["unresolved_queries"]:
            blockers.append(
                {
                    "type": "queries",
                    "description": f"{len(pending['unresolved_queries'])} unresolved queries",
                    "action": "Resolve with: rfd workflow resolve <id> 'answer'",
                }
            )

        # Check validation
        validation = self._get_validation_status()
        if not validation["validation_passing"]:
            blockers.append(
                {
                    "type": "validation",
                    "description": f"{len(validation['validation_failures'])} validation failures",
                    "action": "Fix issues then: rfd validate",
                }
            )

        # Check for locked features
        workflow = self._get_workflow_state()
        if workflow.get("active_workflows"):
            for w in workflow["active_workflows"]:
                if w["locked_by"] and w["locked_at"]:
                    # Check if lock is stale
                    lock_time = datetime.fromisoformat(w["locked_at"])
                    if (datetime.now() - lock_time).seconds > 1800:  # 30 minutes
                        blockers.append(
                            {
                                "type": "stale_lock",
                                "description": f"Feature {w['feature']} has stale lock",
                                "action": f"Clear with: rfd workflow start {w['feature']}",
                            }
                        )

        return blockers

    def _run_health_checks(self) -> Dict[str, bool]:
        """Run system health checks"""
        return {
            "database_exists": Path(self.db_path).exists(),
            "context_dir_exists": (self.rfd.rfd_dir / "context").exists(),
            "project_md_exists": Path("PROJECT.md").exists(),
            "rfd_executable": Path("rfd").exists(),
            "source_intact": len(list(Path("src/rfd").glob("*.py"))) > 10,
            "ai_validator_ready": Path("src/rfd/ai_validator.py").exists(),
            "workflow_ready": Path("src/rfd/workflow_engine.py").exists(),
        }

    def _table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        conn = sqlite3.connect(self.db_path)
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        ).fetchone()
        conn.close()
        return result is not None

    def display_handoff(self):
        """Display handoff information in terminal"""
        handoff = self.generate_handoff()

        print("\n" + "=" * 60)
        print("RFD AUTOMATIC SESSION HANDOFF")
        print("=" * 60)

        # Key Module List
        print("\n🔧 Core Modules Available:")
        modules = [
            ("ai_validator.py", "AI hallucination detection"),
            ("workflow_engine.py", "Gated linear workflow"),
            ("auto_handoff.py", "Automatic resume system"),
            ("speckit_integration.py", "Spec-kit style features"),
            ("session.py", "Session management"),
            ("validation.py", "Reality validation"),
        ]
        for module, desc in modules:
            if Path(f"src/rfd/{module}").exists():
                print(f"   ✅ {module}: {desc}")
            else:
                print(f"   ❌ {module}: MISSING!")

        # System Status
        status = handoff["system_status"]
        print("\n📊 System Status:")
        print(f"   Modules: {status['modules_available']} Python files in src/rfd/")
        print(f"   Features: {status['total_features']} ({status['completion_percentage']:.0f}% complete)")
        print(f"   Hallucinations Caught: {status['hallucinations_caught']}")
        print(f"   Drift Blocked: {status['drift_attempts_blocked']}")

        # Current Session
        session = handoff["current_session"]
        if session:
            print("\n📋 Current Session:")
            if session.get("feature"):
                print(f"   Feature: {session['feature']}")
            if session.get("started"):
                print(f"   Started: {session['started']}")
            if session.get("status"):
                print(f"   Status: {session['status']}")

        # Workflow State
        workflow = handoff["workflow_state"]
        if workflow.get("active_workflows"):
            print("\n🔄 Active Workflows:")
            for w in workflow["active_workflows"]:
                print(f"   {w['feature']}: {w['state']}")

        # Validation Status
        validation = handoff["validation_status"]
        print("\n✅ Validation:")
        print(f"   Validation: {'✅' if validation['validation_passing'] else '❌'}")
        print(f"   Build: {'✅' if validation['build_passing'] else '❌'}")

        # Blockers
        blockers = handoff["blockers"]
        if blockers:
            print("\n⚠️ Blockers:")
            for blocker in blockers:
                print(f"   - {blocker['description']}")
                print(f"     → {blocker['action']}")

        # Next Actions
        actions = handoff["next_actions"]
        if actions:
            print("\n➡️ Next Actions:")
            for i, action in enumerate(actions[:3], 1):
                print(f"   {i}. {action}")

        # Pending Work
        pending = handoff["pending_work"]
        if pending["pending_features"] or pending["pending_tasks"] or pending["unresolved_queries"]:
            print("\n📝 Pending Work:")
            if pending["pending_features"]:
                print(f"   Features: {len(pending['pending_features'])} pending")
            if pending["pending_tasks"]:
                print(f"   Tasks: {len(pending['pending_tasks'])} pending")
            if pending["unresolved_queries"]:
                print(f"   Queries: {len(pending['unresolved_queries'])} unresolved")

        # Health Checks
        health = handoff["system_health"]
        all_healthy = all(health.values())
        print(f"\n🏥 System Health: {'✅ All Green' if all_healthy else '⚠️ Issues Detected'}")
        if not all_healthy:
            for check, passed in health.items():
                if not passed:
                    print(f"   ❌ {check}")

        # Quick Command Reference
        print("\n📋 Quick Commands:")
        commands = [
            ("rfd resume", "Show this handoff"),
            ("rfd status", "Full project status"),
            ("rfd workflow status <feature>", "Check workflow state"),
            ("rfd validate", "Run validation"),
            ("rfd speckit specify <feature>", "Create specification"),
            ("rfd checkpoint <msg>", "Save progress"),
        ]
        for cmd, desc in commands[:6]:
            print(f"   {cmd:<35} # {desc}")

        # What Makes RFD Special
        print("\n🌟 Key Features (Beyond Spec-Kit):")
        print("   • Gated workflow - can't skip phases")
        print("   • AI hallucination detection - catches lies")
        print("   • Session locking - prevents conflicts")
        print("   • Query resolution - forces clarification")
        print("   • Drift prevention - maintains focus")
        print("   • Automatic handoff - no manual docs!")

        print("\n" + "=" * 60)
        print("TO RESUME: Just run 'rfd resume' in new session")
        print("ALL STATE IN: .rfd/memory.db + .rfd/context/")
        print("=" * 60 + "\n")

    def save_to_database(self):
        """Save handoff data to database for persistence"""
        handoff = self.generate_handoff()

        # Custom JSON encoder for datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        conn = sqlite3.connect(self.db_path)

        # Store in memory table
        conn.execute(
            "INSERT OR REPLACE INTO memory (key, value, updated_at) VALUES (?, ?, ?)",
            (
                "last_handoff",
                json.dumps(handoff, cls=DateTimeEncoder),
                datetime.now().isoformat(),
            ),
        )

        conn.commit()
        conn.close()

    def load_from_database(self) -> Dict[str, Any]:
        """Load last handoff from database"""
        conn = sqlite3.connect(self.db_path)

        result = conn.execute("SELECT value FROM memory WHERE key = 'last_handoff'").fetchone()

        conn.close()

        if result:
            return json.loads(result[0])
        return {}

    def handoff(self, from_agent: str, to_agent: str, task: str, context: Optional[Dict] = None) -> int:
        """
        Create agent handoff for QA cycles

        Args:
            from_agent: Agent handing off (e.g., 'coding', 'review', 'qa', 'fix')
            to_agent: Agent receiving handoff
            task: Task description
            context: Optional context data

        Returns:
            Handoff ID
        """
        conn = sqlite3.connect(self.rfd.db_path)

        # Validate agent types
        valid_agents = ["coding", "review", "qa", "fix"]
        if from_agent not in valid_agents or to_agent not in valid_agents:
            conn.close()
            raise ValueError(f"Invalid agent type. Must be one of: {valid_agents}")

        cursor = conn.execute(
            """
            INSERT INTO agent_handoffs (from_agent, to_agent, task_description, context, created_at)
            VALUES (?, ?, ?, ?, datetime('now'))
        """,
            (from_agent, to_agent, task, json.dumps(context or {})),
        )

        handoff_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Log the handoff
        print(f"📋 Handoff #{handoff_id}: {from_agent} → {to_agent}")
        print(f"   Task: {task}")
        if context:
            print(f"   Context: {list(context.keys())}")

        return handoff_id

    def get_pending_handoffs(self, agent_type: str) -> List[Dict[str, Any]]:
        """
        Get pending handoffs for a specific agent type

        Args:
            agent_type: Agent type ('coding', 'review', 'qa', 'fix')

        Returns:
            List of pending handoffs
        """
        conn = sqlite3.connect(self.rfd.db_path)

        handoffs = conn.execute(
            """
            SELECT id, from_agent, task_description, context, created_at
            FROM agent_handoffs
            WHERE to_agent = ? AND status = 'pending'
            ORDER BY created_at
        """,
            (agent_type,),
        ).fetchall()

        conn.close()

        return [
            {"id": h[0], "from": h[1], "task": h[2], "context": json.loads(h[3]) if h[3] else {}, "created": h[4]}
            for h in handoffs
        ]

    def complete_handoff(self, handoff_id: int, result: str = "completed"):
        """
        Mark a handoff as complete

        Args:
            handoff_id: ID of handoff to complete
            result: Result status ('completed', 'failed', 'skipped')
        """
        conn = sqlite3.connect(self.rfd.db_path)

        conn.execute(
            """
            UPDATE agent_handoffs
            SET status = ?, completed_at = datetime('now')
            WHERE id = ?
        """,
            (result, handoff_id),
        )

        conn.commit()
        conn.close()

        print(f"✅ Handoff #{handoff_id} marked as {result}")
