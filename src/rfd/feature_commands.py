"""
Database-first feature management commands for RFD
No more PROJECT.md syncing - database is the single source of truth
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import click


class FeatureManager:
    """Manages features directly in the database - no markdown files!"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self):
        """Ensure the database has the tables we need"""
        conn = sqlite3.connect(self.db_path)
        # Features table already exists, just ensure it's there
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS features (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                acceptance_criteria TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 0,
                assigned_to TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                metadata JSON
            )
        """
        )
        conn.commit()
        conn.close()

    def add_feature(
        self, feature_id: str, description: str, acceptance: str, priority: int = 0, assigned_to: Optional[str] = None
    ) -> bool:
        """Add a new feature to the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
                INSERT INTO features
                (id, description, acceptance_criteria, status, priority,
                 assigned_to, created_at)
                VALUES (?, ?, ?, 'pending', ?, ?, ?)
            """,
                (feature_id, description, acceptance, priority, assigned_to, datetime.now().isoformat()),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Feature already exists
        finally:
            conn.close()

    def list_features(self) -> List[Dict[str, Any]]:
        """List all features from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT id, description, status, priority, assigned_to,
                   created_at, started_at, completed_at
            FROM features
            ORDER BY
                CASE status
                    WHEN 'building' THEN 1
                    WHEN 'testing' THEN 2
                    WHEN 'pending' THEN 3
                    WHEN 'blocked' THEN 4
                    WHEN 'complete' THEN 5
                END,
                priority DESC,
                created_at
        """
        )
        features = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return features

    def get_feature(self, feature_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific feature from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            """
            SELECT * FROM features WHERE id = ?
        """,
            (feature_id,),
        )
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_status(self, feature_id: str, status: str) -> bool:
        """Update feature status in the database"""
        valid_statuses = ["pending", "building", "testing", "complete", "blocked"]
        if status not in valid_statuses:
            return False

        conn = sqlite3.connect(self.db_path)
        timestamp_field = None
        timestamp_value = None

        if status == "building" and timestamp_field is None:
            timestamp_field = "started_at"
            timestamp_value = datetime.now().isoformat()
        elif status == "complete":
            timestamp_field = "completed_at"
            timestamp_value = datetime.now().isoformat()

        if timestamp_field:
            conn.execute(
                f"""
                UPDATE features
                SET status = ?, {timestamp_field} = ?
                WHERE id = ?
            """,
                (status, timestamp_value, feature_id),
            )
        else:
            conn.execute(
                """
                UPDATE features
                SET status = ?
                WHERE id = ?
            """,
                (status, feature_id),
            )

        changes = conn.total_changes
        conn.commit()
        conn.close()
        return changes > 0

    def delete_feature(self, feature_id: str) -> bool:
        """Delete a feature from the database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM features WHERE id = ?", (feature_id,))
        changes = conn.total_changes
        conn.commit()
        conn.close()
        return changes > 0

    def get_progress_summary(self) -> Dict[str, int]:
        """Get feature progress summary from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            """
            SELECT status, COUNT(*) as count
            FROM features
            GROUP BY status
        """
        )

        summary = {"total": 0}
        for row in cursor:
            summary[row[0]] = row[1]
            summary["total"] += row[1]

        conn.close()
        return summary


def create_feature_commands(cli, rfd_class):
    """Create the feature command group for the CLI"""

    @cli.group(invoke_without_command=True)
    @click.pass_context
    def feature(ctx):
        """Feature management (database-driven, no PROJECT.md!)"""
        if ctx.invoked_subcommand is None:
            # Default: list all features
            ctx.invoke(feature_list)

    @feature.command("add")
    @click.argument("feature_id")
    @click.option("--description", "-d", required=True, help="Feature description")
    @click.option("--acceptance", "-a", help="Acceptance criteria")
    @click.option("--priority", "-p", type=int, default=0, help="Priority (0-10)")
    @click.option("--assign", help="Assign to developer")
    @click.pass_context
    def feature_add(ctx, feature_id, description, acceptance, priority, assign):
        """Add a new feature to the database"""
        rfd = rfd_class()
        manager = FeatureManager(rfd.db_path)

        if not acceptance:
            acceptance = f"{description} is complete and working"

        if manager.add_feature(feature_id, description, acceptance, priority, assign):
            click.echo(f"✅ Added feature '{feature_id}' to database")
            click.echo(f"   Description: {description}")
            click.echo(f"   Acceptance: {acceptance}")
            if priority > 0:
                click.echo(f"   Priority: {priority}")
            if assign:
                click.echo(f"   Assigned to: {assign}")
            click.echo(f"\nNext: rfd session start {feature_id}")
        else:
            click.echo(f"❌ Feature '{feature_id}' already exists")

    @feature.command("list")
    @click.option("--status", help="Filter by status")
    @click.option("--format", type=click.Choice(["table", "json"]), default="table")
    @click.pass_context
    def feature_list(ctx, status, format):
        """List all features from the database"""
        rfd = rfd_class()
        manager = FeatureManager(rfd.db_path)
        features = manager.list_features()

        if status:
            features = [f for f in features if f["status"] == status]

        if format == "json":
            import json

            click.echo(json.dumps(features, indent=2))
        else:
            if not features:
                click.echo("No features found")
                return

            # Group by status
            by_status = {}
            for f in features:
                s = f["status"]
                if s not in by_status:
                    by_status[s] = []
                by_status[s].append(f)

            # Display
            click.echo("\n📦 Features (from database):\n")

            status_order = ["building", "testing", "pending", "blocked", "complete"]
            status_icons = {"building": "🔨", "testing": "🧪", "pending": "⏳", "blocked": "🚫", "complete": "✅"}

            for status in status_order:
                if status in by_status:
                    click.echo(f"{status_icons.get(status, '📦')} {status.upper()}:")
                    for f in by_status[status]:
                        priority_str = f" [P{f['priority']}]" if f["priority"] > 0 else ""
                        assigned_str = f" @{f['assigned_to']}" if f["assigned_to"] else ""
                        click.echo(f"   {f['id']}: {f['description']}{priority_str}{assigned_str}")
                    click.echo()

    @feature.command("show")
    @click.argument("feature_id")
    @click.pass_context
    def feature_show(ctx, feature_id):
        """Show details of a specific feature"""
        rfd = rfd_class()
        manager = FeatureManager(rfd.db_path)
        feature = manager.get_feature(feature_id)

        if not feature:
            click.echo(f"❌ Feature '{feature_id}' not found")
            return

        status_icons = {"pending": "⏳", "building": "🔨", "testing": "🧪", "complete": "✅", "blocked": "🚫"}

        click.echo(f"\n{status_icons.get(feature['status'], '📦')} Feature: {feature['id']}")
        click.echo("=" * 50)
        click.echo(f"Description: {feature['description']}")
        click.echo(f"Acceptance: {feature['acceptance_criteria']}")
        click.echo(f"Status: {feature['status']}")
        if feature["priority"] > 0:
            click.echo(f"Priority: {feature['priority']}")
        if feature["assigned_to"]:
            click.echo(f"Assigned to: {feature['assigned_to']}")
        if feature["created_at"]:
            click.echo(f"Created: {feature['created_at']}")
        if feature["started_at"]:
            click.echo(f"Started: {feature['started_at']}")
        if feature["completed_at"]:
            click.echo(f"Completed: {feature['completed_at']}")

    @feature.command("start")
    @click.argument("feature_id")
    @click.pass_context
    def feature_start(ctx, feature_id):
        """Start working on a feature"""
        rfd = rfd_class()
        manager = FeatureManager(rfd.db_path)

        if manager.update_status(feature_id, "building"):
            click.echo(f"🔨 Started working on feature '{feature_id}'")
            # Also start a session
            ctx.invoke(ctx.parent.parent.command.get_command(ctx.parent.parent, "session"), "start", feature_id)
        else:
            click.echo(f"❌ Failed to start feature '{feature_id}'")

    @feature.command("complete")
    @click.argument("feature_id")
    @click.pass_context
    def feature_complete(ctx, feature_id):
        """Mark a feature as complete"""
        rfd = rfd_class()
        manager = FeatureManager(rfd.db_path)

        if manager.update_status(feature_id, "complete"):
            click.echo(f"✅ Feature '{feature_id}' marked as complete")

            # Show progress
            summary = manager.get_progress_summary()
            complete_pct = (summary.get("complete", 0) / summary["total"] * 100) if summary["total"] > 0 else 0
            click.echo(f"\n📊 Progress: {complete_pct:.1f}% complete")
            click.echo(f"   {summary.get('complete', 0)}/{summary['total']} features done")
        else:
            click.echo(f"❌ Failed to complete feature '{feature_id}'")

    @feature.command("block")
    @click.argument("feature_id")
    @click.option("--reason", help="Reason for blocking")
    @click.pass_context
    def feature_block(ctx, feature_id, reason):
        """Mark a feature as blocked"""
        rfd = rfd_class()
        manager = FeatureManager(rfd.db_path)

        if manager.update_status(feature_id, "blocked"):
            click.echo(f"🚫 Feature '{feature_id}' marked as blocked")
            if reason:
                click.echo(f"   Reason: {reason}")
        else:
            click.echo(f"❌ Failed to block feature '{feature_id}'")

    @feature.command("delete")
    @click.argument("feature_id")
    @click.confirmation_option(prompt="Are you sure you want to delete this feature?")
    @click.pass_context
    def feature_delete(ctx, feature_id):
        """Delete a feature from the database"""
        rfd = rfd_class()
        manager = FeatureManager(rfd.db_path)

        if manager.delete_feature(feature_id):
            click.echo(f"🗑️  Deleted feature '{feature_id}'")
        else:
            click.echo(f"❌ Failed to delete feature '{feature_id}'")

    @feature.command("progress")
    @click.pass_context
    def feature_progress(ctx):
        """Show overall feature progress"""
        rfd = rfd_class()
        manager = FeatureManager(rfd.db_path)
        summary = manager.get_progress_summary()

        if summary["total"] == 0:
            click.echo("No features defined yet")
            return

        complete_pct = (summary.get("complete", 0) / summary["total"] * 100) if summary["total"] > 0 else 0

        click.echo("\n📊 Feature Progress (from database):")
        click.echo("=" * 50)
        click.echo(f"Total: {summary['total']} features")
        click.echo(f"Progress: {complete_pct:.1f}% complete\n")

        if "complete" in summary:
            click.echo(f"   ✅ Complete: {summary['complete']}")
        if "building" in summary:
            click.echo(f"   🔨 Building: {summary['building']}")
        if "testing" in summary:
            click.echo(f"   🧪 Testing: {summary['testing']}")
        if "pending" in summary:
            click.echo(f"   ⏳ Pending: {summary['pending']}")
        if "blocked" in summary:
            click.echo(f"   🚫 Blocked: {summary['blocked']}")

    return feature
