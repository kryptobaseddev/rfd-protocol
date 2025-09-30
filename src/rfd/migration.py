"""
RFD Migration System
Handles updates to .rfd/ structure when RFD itself is upgraded
"""

import json
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class RFDMigration:
    """Handles migrations of .rfd/ directory structure across RFD versions"""

    def __init__(self, project_root: Path = Path(".")):
        self.project_root = project_root
        self.rfd_dir = project_root / ".rfd"
        self.version_file = self.rfd_dir / "version.json"

    def get_rfd_version(self) -> str:
        """Get current RFD package version"""
        try:
            from . import __version__

            return __version__
        except Exception:
            return "1.0.0"

    def get_project_rfd_version(self) -> str:
        """Get the RFD version this project was initialized with"""
        if self.version_file.exists():
            with open(self.version_file) as f:
                data = json.load(f)
                return data.get("rfd_version", "0.0.0")
        return "0.0.0"

    def needs_migration(self) -> bool:
        """Check if project needs migration"""
        if not self.rfd_dir.exists():
            return False

        current = self.get_rfd_version()
        project = self.get_project_rfd_version()

        # Simple version comparison (could be more sophisticated)
        return current != project

    def backup_before_migration(self) -> Path:
        """Create backup of .rfd/ before migration"""
        backup_dir = self.project_root / f".rfd.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if self.rfd_dir.exists():
            shutil.copytree(self.rfd_dir, backup_dir)
        return backup_dir

    def migrate(self) -> Dict[str, Any]:
        """Run all necessary migrations"""
        if not self.needs_migration():
            return {"status": "up_to_date", "version": self.get_rfd_version()}

        # Backup first
        backup_path = self.backup_before_migration()

        results = {
            "status": "migrated",
            "from_version": self.get_project_rfd_version(),
            "to_version": self.get_rfd_version(),
            "backup": str(backup_path),
            "migrations": [],
        }

        try:
            # Run version-specific migrations
            self._migrate_database_schema()
            self._migrate_context_structure()
            self._update_version_file()

            results["migrations"].append("database_schema")
            results["migrations"].append("context_structure")

        except Exception as e:
            # Rollback on error
            if backup_path.exists():
                shutil.rmtree(self.rfd_dir, ignore_errors=True)
                shutil.move(backup_path, self.rfd_dir)

            results["status"] = "failed"
            results["error"] = str(e)

        return results

    def _migrate_database_schema(self):
        """Update database schema if needed"""
        db_path = self.rfd_dir / "memory.db"
        if not db_path.exists():
            return

        conn = sqlite3.connect(db_path)

        # Add new tables/columns as RFD evolves
        # Example: Adding a new migrations table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rfd_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                applied_at TEXT NOT NULL,
                description TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def _migrate_context_structure(self):
        """Update context directory structure if needed"""
        context_dir = self.rfd_dir / "context"
        if not context_dir.exists():
            context_dir.mkdir(parents=True, exist_ok=True)

        # Ensure all required subdirectories exist
        (context_dir / "checkpoints").mkdir(exist_ok=True)

        # Migrate old file formats if needed
        # Example: Convert old memory format to new
        old_memory = context_dir / "memory.txt"
        new_memory = context_dir / "memory.json"

        if old_memory.exists() and not new_memory.exists():
            # Convert old format to JSON
            with open(old_memory) as f:
                content = f.read()

            memory_data = {
                "legacy_content": content,
                "migrated_at": datetime.now().isoformat(),
                "version": self.get_rfd_version(),
            }

            with open(new_memory, "w") as f:
                json.dump(memory_data, f, indent=2)

            # Keep old file as backup
            old_memory.rename(old_memory.with_suffix(".txt.bak"))

    def _update_version_file(self):
        """Update version tracking file"""
        version_data = {
            "rfd_version": self.get_rfd_version(),
            "updated_at": datetime.now().isoformat(),
            "project_root": str(self.project_root.resolve()),
        }

        with open(self.version_file, "w") as f:
            json.dump(version_data, f, indent=2)

    def check_compatibility(self) -> Dict[str, Any]:
        """Check if current RFD version is compatible with project"""
        current = self.get_rfd_version()
        project = self.get_project_rfd_version()

        # Define breaking change versions
        breaking_changes = {
            "2.0.0": "Major rewrite - manual migration required",
            "1.5.0": "Database schema changes",
        }

        result = {
            "compatible": True,
            "current_version": current,
            "project_version": project,
            "warnings": [],
        }

        # Check for breaking changes
        for breaking_version, description in breaking_changes.items():
            if self._version_greater_than(current, breaking_version) and self._version_less_than(
                project, breaking_version
            ):
                result["compatible"] = False
                result["warnings"].append(f"Breaking change at v{breaking_version}: {description}")

        return result

    def _version_greater_than(self, v1: str, v2: str) -> bool:
        """Compare version strings"""
        v1_parts = [int(x) for x in v1.split(".")]
        v2_parts = [int(x) for x in v2.split(".")]
        return v1_parts > v2_parts

    def _version_less_than(self, v1: str, v2: str) -> bool:
        """Compare version strings"""
        v1_parts = [int(x) for x in v1.split(".")]
        v2_parts = [int(x) for x in v2.split(".")]
        return v1_parts < v2_parts

    def create_qa_tables(self, db_path: Path = None):
        """Create tables for QA cycles and review results"""
        if db_path is None:
            db_path = self.rfd_dir / "memory.db"

        conn = sqlite3.connect(db_path)

        # Create qa_cycles table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS qa_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feature_id TEXT NOT NULL,
                cycle_number INTEGER NOT NULL,
                status TEXT NOT NULL,
                started_at DATETIME NOT NULL,
                completed_at DATETIME,
                FOREIGN KEY (feature_id) REFERENCES features(id)
            )
        """
        )

        # Create review_results table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS review_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_id INTEGER NOT NULL,
                review_type TEXT NOT NULL,
                passed BOOLEAN NOT NULL,
                issues TEXT,
                suggestions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cycle_id) REFERENCES qa_cycles(id)
            )
        """
        )

        # Create agent_handoffs table
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
        conn.close()
    
    def create_prevention_tables(self, db_path: Path = None):
        """Create tables for prevention system"""
        if db_path is None:
            db_path = self.rfd_dir / "memory.db"
        
        conn = sqlite3.connect(db_path)
        
        # Create workflows table for workflow specifications
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                spec JSON,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Add missing columns to features table if they don't exist
        try:
            conn.execute("ALTER TABLE features ADD COLUMN name TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            conn.execute("ALTER TABLE features ADD COLUMN scope_definition JSON")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Create prevention_stats table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prevention_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                validation_type TEXT,
                violations JSON,
                prevented BOOLEAN,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
