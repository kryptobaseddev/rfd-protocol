"""
Feature Manager for RFD
Handles feature lifecycle, status tracking, and database synchronization
Production-ready implementation that eliminates manual PROJECT.md editing
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

import frontmatter


class FeatureManager:
    """Manages features through their complete lifecycle"""

    def __init__(self, rfd):
        self.rfd = rfd
        self.db_path = rfd.db_path
        self._ensure_tables()
        self._sync_from_spec()

    def _ensure_tables(self):
        """Ensure all required database tables exist"""
        conn = sqlite3.connect(self.db_path)

        # Check if features table exists and has all columns
        cursor = conn.execute("PRAGMA table_info(features)")
        columns = {row[1] for row in cursor.fetchall()}

        if not columns:
            # Create new table
            conn.execute(
                """
                CREATE TABLE features (
                    id TEXT PRIMARY KEY,
                    description TEXT,
                    acceptance_criteria TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    assigned_to TEXT,
                    priority INTEGER DEFAULT 0,
                    tags JSON,
                    metadata JSON
                )
            """
            )
        else:
            # Add missing columns
            if "started_at" not in columns:
                conn.execute("ALTER TABLE features ADD COLUMN started_at TEXT")
            if "acceptance_criteria" not in columns:
                conn.execute("ALTER TABLE features ADD COLUMN acceptance_criteria TEXT")
            if "assigned_to" not in columns:
                conn.execute("ALTER TABLE features ADD COLUMN assigned_to TEXT")
            if "priority" not in columns:
                conn.execute("ALTER TABLE features ADD COLUMN priority INTEGER DEFAULT 0")
            if "tags" not in columns:
                conn.execute("ALTER TABLE features ADD COLUMN tags JSON")
            if "metadata" not in columns:
                conn.execute("ALTER TABLE features ADD COLUMN metadata JSON")

        # Feature progress tracking
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feature_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_id TEXT,
                timestamp TEXT,
                event_type TEXT,  -- started, progress, blocked, completed
                message TEXT,
                data JSON,
                FOREIGN KEY (feature_id) REFERENCES features(id)
            )
        """
        )

        # Project phases
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS project_phases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                status TEXT DEFAULT 'pending',
                started_at TEXT,
                completed_at TEXT,
                order_index INTEGER
            )
        """
        )

        # Tasks within features
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_id TEXT,
                description TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (feature_id) REFERENCES features(id)
            )
        """
        )

        conn.commit()
        conn.close()

    def _sync_from_spec(self):
        """Sync features from PROJECT.md to database"""
        spec = self.rfd.load_project_spec()
        features = spec.get("features", [])

        conn = sqlite3.connect(self.db_path)

        for feature in features:
            # Check if feature exists
            existing = conn.execute("SELECT id FROM features WHERE id = ?", (feature.get("id"),)).fetchone()

            if not existing:
                # Insert new feature
                conn.execute(
                    """
                    INSERT INTO features (
                        id, description, acceptance_criteria, status, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        feature.get("id"),
                        feature.get("description"),
                        feature.get("acceptance", ""),
                        feature.get("status", "pending"),
                        datetime.now().isoformat(),
                    ),
                )
            else:
                # Update existing feature status from PROJECT.md only if newer
                conn.execute(
                    """
                    UPDATE features
                    SET status = ?
                    WHERE id = ? AND status != ?
                """,
                    (
                        feature.get("status", "pending"),
                        feature.get("id"),
                        feature.get("status", "pending"),
                    ),
                )

        conn.commit()
        conn.close()

    def start_feature(self, feature_id: str) -> bool:
        """Start working on a feature"""
        conn = sqlite3.connect(self.db_path)

        # Update feature status
        conn.execute(
            """
            UPDATE features
            SET status = 'in_progress',
                started_at = ?
            WHERE id = ?
        """,
            (datetime.now().isoformat(), feature_id),
        )

        # Log progress event
        conn.execute(
            """
            INSERT INTO feature_progress (
                feature_id, timestamp, event_type, message
            ) VALUES (?, ?, ?, ?)
        """,
            (
                feature_id,
                datetime.now().isoformat(),
                "started",
                f"Started work on {feature_id}",
            ),
        )

        conn.commit()
        conn.close()

        # Update PROJECT.md
        self._update_project_md(feature_id, "in_progress")
        return True

    def complete_feature(self, feature_id: str, evidence: Optional[Dict] = None) -> bool:
        """Mark feature as complete"""
        conn = sqlite3.connect(self.db_path)

        # Validate acceptance criteria if possible
        if evidence and not self._validate_acceptance(feature_id, evidence):
            conn.execute(
                """
                INSERT INTO feature_progress (
                    feature_id, timestamp, event_type, message, data
                ) VALUES (?, ?, ?, ?, ?)
            """,
                (
                    feature_id,
                    datetime.now().isoformat(),
                    "blocked",
                    "Acceptance criteria not met",
                    json.dumps(evidence),
                ),
            )
            conn.commit()
            conn.close()
            return False

        # Update feature status
        conn.execute(
            """
            UPDATE features
            SET status = 'complete',
                completed_at = ?
            WHERE id = ?
        """,
            (datetime.now().isoformat(), feature_id),
        )

        # Log completion
        conn.execute(
            """
            INSERT INTO feature_progress (
                feature_id, timestamp, event_type, message, data
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                feature_id,
                datetime.now().isoformat(),
                "completed",
                f"Feature {feature_id} completed successfully",
                json.dumps(evidence) if evidence else None,
            ),
        )

        conn.commit()
        conn.close()

        # Update PROJECT.md
        self._update_project_md(feature_id, "complete")
        return True

    def update_progress(self, feature_id: str, message: str, data: Optional[Dict] = None):
        """Update feature progress"""
        conn = sqlite3.connect(self.db_path)

        conn.execute(
            """
            INSERT INTO feature_progress (
                feature_id, timestamp, event_type, message, data
            ) VALUES (?, ?, ?, ?, ?)
        """,
            (
                feature_id,
                datetime.now().isoformat(),
                "progress",
                message,
                json.dumps(data) if data else None,
            ),
        )

        conn.commit()
        conn.close()

    def get_feature_status(self, feature_id: str) -> Dict:
        """Get complete feature status from database"""
        conn = sqlite3.connect(self.db_path)

        # Get feature details
        feature = conn.execute(
            """
            SELECT id, description, acceptance_criteria, status,
                   created_at, started_at, completed_at
            FROM features WHERE id = ?
        """,
            (feature_id,),
        ).fetchone()

        if not feature:
            return {}

        # Get progress history
        progress = conn.execute(
            """
            SELECT timestamp, event_type, message, data
            FROM feature_progress
            WHERE feature_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        """,
            (feature_id,),
        ).fetchall()

        # Get related tasks
        tasks = conn.execute(
            """
            SELECT description, status, completed_at
            FROM tasks
            WHERE feature_id = ?
            ORDER BY created_at
        """,
            (feature_id,),
        ).fetchall()

        conn.close()

        return {
            "id": feature[0],
            "description": feature[1],
            "acceptance_criteria": feature[2],
            "status": feature[3],
            "created_at": feature[4],
            "started_at": feature[5],
            "completed_at": feature[6],
            "progress": [
                {
                    "timestamp": p[0],
                    "event_type": p[1],
                    "message": p[2],
                    "data": json.loads(p[3]) if p[3] else None,
                }
                for p in progress
            ],
            "tasks": [{"description": t[0], "status": t[1], "completed_at": t[2]} for t in tasks],
        }

    def get_all_features(self) -> List[Dict]:
        """Get all features with their current status"""
        conn = sqlite3.connect(self.db_path)

        features = conn.execute(
            """
            SELECT id, description, status, started_at, completed_at
            FROM features
            ORDER BY
                CASE status
                    WHEN 'in_progress' THEN 1
                    WHEN 'pending' THEN 2
                    WHEN 'complete' THEN 3
                    ELSE 4
                END
        """
        ).fetchall()

        conn.close()

        return [
            {
                "id": f[0],
                "description": f[1],
                "status": f[2],
                "started_at": f[3],
                "completed_at": f[4],
            }
            for f in features
        ]

    def add_task(self, feature_id: str, description: str) -> int:
        """Add a task to a feature"""
        conn = sqlite3.connect(self.db_path)

        cursor = conn.execute(
            """
            INSERT INTO tasks (feature_id, description, created_at)
            VALUES (?, ?, ?)
        """,
            (feature_id, description, datetime.now().isoformat()),
        )

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return task_id

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as complete"""
        conn = sqlite3.connect(self.db_path)

        conn.execute(
            """
            UPDATE tasks
            SET status = 'complete',
                completed_at = ?
            WHERE id = ?
        """,
            (datetime.now().isoformat(), task_id),
        )

        conn.commit()
        conn.close()
        return True

    def _validate_acceptance(self, feature_id: str, evidence: Dict) -> bool:
        """Validate feature acceptance criteria"""
        conn = sqlite3.connect(self.db_path)

        result = conn.execute("SELECT acceptance_criteria FROM features WHERE id = ?", (feature_id,)).fetchone()

        conn.close()

        if not result or not result[0]:
            return True  # No criteria means auto-accept

        criteria = result[0]

        # Check for test-based acceptance
        if "test" in criteria.lower():
            tests_passed = evidence.get("tests_passed", False)
            return tests_passed

        # Default to accepting if evidence provided
        return bool(evidence)

    def _update_project_md(self, feature_id: str, new_status: str):
        """Update PROJECT.md to reflect database state"""
        project_file = self.rfd.root / "PROJECT.md"

        if not project_file.exists():
            return

        # Read current content
        with open(project_file) as f:
            post = frontmatter.load(f)

        # Update feature status in metadata
        features = post.metadata.get("features", [])
        for feature in features:
            if feature.get("id") == feature_id:
                feature["status"] = new_status
                break

        # Write back
        with open(project_file, "w") as f:
            f.write(frontmatter.dumps(post))

    def get_project_phases(self) -> List[Dict]:
        """Get project phases"""
        conn = sqlite3.connect(self.db_path)

        phases = conn.execute(
            """
            SELECT id, name, description, status, started_at, completed_at
            FROM project_phases
            ORDER BY order_index
        """
        ).fetchall()

        conn.close()

        return [
            {
                "id": p[0],
                "name": p[1],
                "description": p[2],
                "status": p[3],
                "started_at": p[4],
                "completed_at": p[5],
            }
            for p in phases
        ]

    def create_phase(self, name: str, description: str, order: int = 0) -> int:
        """Create a new project phase"""
        conn = sqlite3.connect(self.db_path)

        cursor = conn.execute(
            """
            INSERT INTO project_phases (name, description, order_index)
            VALUES (?, ?, ?)
        """,
            (name, description, order),
        )

        phase_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return phase_id

    def get_dashboard(self) -> Dict:
        """Get complete project dashboard data"""
        features = self.get_all_features()
        phases = self.get_project_phases()

        # Calculate statistics
        total_features = len(features)
        completed = sum(1 for f in features if f["status"] == "complete")
        in_progress = sum(1 for f in features if f["status"] == "in_progress")
        pending = sum(1 for f in features if f["status"] == "pending")

        return {
            "statistics": {
                "total_features": total_features,
                "completed": completed,
                "in_progress": in_progress,
                "pending": pending,
                "completion_rate": ((completed / total_features * 100) if total_features > 0 else 0),
            },
            "features": features,
            "phases": phases,
            "current_focus": next((f for f in features if f["status"] == "in_progress"), None),
        }
