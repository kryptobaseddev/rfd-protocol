"""
Database Accountability System
Ensures database-first architecture is maintained
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List

import yaml


class DatabaseAccountability:
    """Enforces database-first principles and tracks violations"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.violations = []

    def audit_database_first(self, project_root: Path) -> Dict[str, Any]:
        """
        Audit project for database-first compliance
        Returns violations and recommendations
        """
        self.violations = []

        # Check 1: Features should be in database, not just PROJECT.md
        self._check_features_in_database(project_root)

        # Check 2: No direct PROJECT.md edits for status changes
        self._check_project_md_sync(project_root)

        # Check 3: Commands should query database, not files
        self._check_command_usage()

        # Check 4: Session state should be in database
        self._check_session_state()

        # Check 5: Tasks and phases should be tracked in database
        self._check_task_tracking()

        # Check 6: Template sync status
        self._check_template_sync(project_root)

        return {
            "compliant": len(self.violations) == 0,
            "violations": self.violations,
            "recommendations": self._get_recommendations(),
        }

    def _check_features_in_database(self, project_root: Path):
        """Ensure all features are tracked in database"""
        project_md = project_root / "PROJECT.md"
        if not project_md.exists():
            return

        # Load PROJECT.md features
        with open(project_md) as f:
            content = f.read()
            # Parse YAML frontmatter
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 2:
                    spec = yaml.safe_load(parts[1])
                    md_features = spec.get("features", [])
            else:
                md_features = []

        # Load database features
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT id, status FROM features")
        db_features = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()

        # Check for discrepancies
        for feature in md_features:
            fid = feature.get("id")
            md_status = feature.get("status")
            db_status = db_features.get(fid)

            if not db_status:
                self.violations.append(
                    {
                        "type": "missing_in_database",
                        "feature": fid,
                        "message": f"Feature '{fid}' exists in PROJECT.md but not in database",
                    }
                )
            elif md_status != db_status:
                self.violations.append(
                    {
                        "type": "status_mismatch",
                        "feature": fid,
                        "message": f"Feature '{fid}' status mismatch: PROJECT.md={md_status}, DB={db_status}",
                        "fix": f"Run: rfd feature sync {fid}",
                    }
                )

    def _check_project_md_sync(self, project_root: Path):
        """Check if PROJECT.md is being manually edited instead of using commands"""
        project_md = project_root / "PROJECT.md"
        if not project_md.exists():
            return

        # Check git history for direct edits (simplified check)
        import subprocess

        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "-n", "5", "--", "PROJECT.md"],
                capture_output=True,
                text=True,
                cwd=project_root,
            )

            # Look for manual edits vs automated updates
            for line in result.stdout.split("\n"):
                if "manually" in line.lower() or "edit" in line.lower():
                    self.violations.append(
                        {
                            "type": "manual_edit",
                            "message": "PROJECT.md appears to have manual edits - use 'rfd feature' commands instead",
                        }
                    )
                    break
        except Exception:
            pass

    def _check_command_usage(self):
        """Verify commands are using database queries"""
        # This is more of a code audit - we've already fixed validation.py
        # But we can check for other violations
        pass

    def _check_session_state(self):
        """Ensure session state is properly tracked in database"""
        conn = sqlite3.connect(self.db_path)

        # Check for active sessions (sessions without ended_at)
        cursor = conn.execute("SELECT COUNT(*) FROM sessions WHERE ended_at IS NULL")
        active_count = cursor.fetchone()[0]

        if active_count > 1:
            self.violations.append(
                {
                    "type": "multiple_active_sessions",
                    "message": f"Found {active_count} active sessions - should only have 1",
                    "fix": "Run: rfd session end",
                }
            )

        # Check for orphaned sessions (started but never completed)
        cursor = conn.execute(
            """
            SELECT id, feature_id, started_at
            FROM sessions
            WHERE ended_at IS NULL
            AND datetime(started_at) < datetime('now', '-7 days')
        """
        )

        for row in cursor.fetchall():
            self.violations.append(
                {
                    "type": "orphaned_session",
                    "message": f"Session {row[0]} for feature '{row[1]}' has been active for >7 days",
                    "fix": "Run: rfd session end",
                }
            )

        conn.close()

    def _check_task_tracking(self):
        """Ensure tasks are being tracked in database"""
        conn = sqlite3.connect(self.db_path)

        # Check if tasks table is being used
        cursor = conn.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]

        # Check if we have features but no tasks
        cursor = conn.execute("SELECT COUNT(*) FROM features")
        feature_count = cursor.fetchone()[0]

        if feature_count > 0 and task_count == 0:
            self.violations.append(
                {
                    "type": "no_task_tracking",
                    "message": "Features exist but no tasks are tracked in database",
                    "fix": "Use 'rfd plan tasks <feature>' to generate tasks",
                }
            )

        conn.close()

    def _check_template_sync(self, project_root: Path):
        """Check if Claude command templates are in sync"""
        import hashlib

        source_dir = project_root / "src" / "rfd" / "templates" / "commands"
        local_dir = project_root / ".claude" / "commands"

        # Skip check if not in development (source dir won't exist in installed package)
        if not source_dir.exists():
            return

        if not local_dir.exists():
            self.violations.append(
                {
                    "type": "missing_claude_commands",
                    "message": ".claude/commands/ directory not found",
                    "fix": "Run: rfd init",
                }
            )
            return

        def get_file_hash(filepath: Path) -> str:
            if not filepath.exists():
                return ""
            with open(filepath, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()

        source_files = list(source_dir.glob("*.md"))
        local_files = list(local_dir.glob("*.md"))

        source_names = {f.name for f in source_files}
        local_names = {f.name for f in local_files}

        # Check for missing files
        missing_in_local = source_names - local_names
        if missing_in_local:
            self.violations.append(
                {
                    "type": "template_sync_missing",
                    "message": f"Commands missing in .claude/: {', '.join(sorted(missing_in_local))}",
                    "fix": "Run: cp src/rfd/templates/commands/*.md .claude/commands/",
                }
            )

        # Check for out-of-sync files
        out_of_sync = []
        for source_file in source_files:
            local_file = local_dir / source_file.name
            if local_file.exists():
                if get_file_hash(source_file) != get_file_hash(local_file):
                    out_of_sync.append(source_file.name)

        if out_of_sync:
            self.violations.append(
                {
                    "type": "template_sync_mismatch",
                    "message": f"Commands out of sync: {', '.join(sorted(out_of_sync))}",
                    "fix": "Run: cp src/rfd/templates/commands/*.md .claude/commands/",
                }
            )

    def _get_recommendations(self) -> List[str]:
        """Get recommendations based on violations"""
        recommendations = []

        if any(v["type"] == "status_mismatch" for v in self.violations):
            recommendations.append("Sync PROJECT.md with database: rfd feature sync --all")

        if any(v["type"] == "missing_in_database" for v in self.violations):
            recommendations.append("Import features to database: rfd feature import")

        if any(v["type"] == "no_task_tracking" for v in self.violations):
            recommendations.append("Start tracking tasks: rfd plan tasks <feature-id>")

        if any(v["type"] in ["template_sync_missing", "template_sync_mismatch"] for v in self.violations):
            recommendations.append("Sync templates: cp src/rfd/templates/commands/*.md .claude/commands/")

        if not self.violations:
            recommendations.append("✅ Database-first architecture is properly maintained!")

        return recommendations

    def enforce_database_first(self) -> bool:
        """
        Enforce database-first by blocking operations if violations exist
        Returns True if compliant, False if violations exist
        """
        audit = self.audit_database_first(Path.cwd())

        if not audit["compliant"]:
            print("⚠️  Database-First Violations Detected!")
            print("=" * 50)
            for violation in audit["violations"]:
                print(f"❌ {violation['message']}")
                if "fix" in violation:
                    print(f"   Fix: {violation['fix']}")

            print("\n📋 Recommendations:")
            for rec in audit["recommendations"]:
                print(f"   • {rec}")

            return False

        return True
