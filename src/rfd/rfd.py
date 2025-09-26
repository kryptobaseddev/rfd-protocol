#!/usr/bin/env python3
"""
RFD: Reality-First Development System
Single entry point for all development operations
"""

import json
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from .build import BuildEngine
from .db_utils import get_db_connection, init_database
from .project_updater import ProjectUpdater
from .session import SessionManager
from .spec import SpecEngine
from .validation import ValidationEngine


class RFD:
    """Main RFD orchestrator - coordinates all subsystems"""

    def __init__(self):
        self.root = Path.cwd()
        self.rfd_dir = self.root / ".rfd"
        self.db_path = self.rfd_dir / "memory.db"

        # Initialize subsystems
        self._init_structure()
        self._init_database()

        # Load modules with proper imports
        self.builder = BuildEngine(self)
        self.validator = ValidationEngine(self)
        self.spec = SpecEngine(self)
        self.session = SessionManager(self)
        self.project_updater = ProjectUpdater(self)

        # Add workflow engine for gated progression
        from .workflow_engine import GatedWorkflow

        self.workflow = GatedWorkflow(self)

        # Add spec-kit integration
        from .speckit_integration import SpecKitIntegration

        self.speckit = SpecKitIntegration(self)

    def _init_structure(self):
        """Create RFD directory structure"""
        self.rfd_dir.mkdir(exist_ok=True)
        (self.rfd_dir / "context").mkdir(exist_ok=True)
        (self.rfd_dir / "context" / "checkpoints").mkdir(exist_ok=True)

    def _init_database(self):
        """Initialize SQLite with WAL mode for state management"""
        # Use new database utilities for WAL mode and proper setup
        init_database(self.db_path)
        # migrate_to_wal is already handled in get_db_connection calls

        # Get connection with WAL mode
        conn = get_db_connection(self.db_path)
        try:
            # Core tables
            conn.executescript(
                """
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

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                started_at TEXT,
                ended_at TEXT,
                feature_id TEXT,
                success BOOLEAN,
                changes JSON,
                errors JSON
            );

            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value JSON,
                updated_at TEXT
            );
        """
            )
            conn.commit()
        finally:
            conn.close()

    def load_project_spec(self) -> Dict[str, Any]:
        """Load project spec from database and config.yaml"""
        from .config_manager import ConfigManager
        from .db_utils import get_db_connection

        # Get config from config.yaml
        config_mgr = ConfigManager(self.rfd_dir)
        config = config_mgr.load_config() or {}

        # Get features from database
        conn = get_db_connection(self.db_path)
        features = []

        try:
            cursor = conn.execute(
                """SELECT id, description, acceptance_criteria, status
                   FROM features ORDER BY created_at"""
            )
            for row in cursor.fetchall():
                features.append(
                    {"id": row[0], "description": row[1], "acceptance": row[2] or "Not specified", "status": row[3]}
                )
        finally:
            conn.close()

        # Combine config and features
        spec = {
            "name": config.get("project", {}).get("name", "Unknown Project"),
            "description": config.get("project", {}).get("description", ""),
            "version": config.get("project", {}).get("rfd_version", "1.0.0"),
            "stack": config.get("stack", {}),
            "rules": config.get("rules", {}),
            "constraints": config.get("constraints", []),
            "features": features,
        }

        return spec

    def get_current_state(self) -> Dict[str, Any]:
        """Get complete current project state"""
        return {
            "spec": self.load_project_spec(),
            "validation": self.validator.get_status(),
            "build": self.builder.get_status(),
            "session": self.session.get_current(),
            "features": self.get_features_status(),
        }

    def save_project_spec(self, spec: Dict[str, Any]) -> None:
        """DEPRECATED - Project spec now lives in database and config.yaml"""
        import yaml

        project_file = self.root / "PROJECT.md"

        # Separate frontmatter from content
        content = ""
        if project_file.exists():
            with open(project_file) as f:
                full_content = f.read()
                # Extract existing content after frontmatter
                parts = full_content.split("---\n", 2)
                if len(parts) > 2:
                    content = parts[2]
                elif len(parts) == 1 and not full_content.startswith("---"):
                    content = full_content

        # Write updated spec with frontmatter
        with open(project_file, "w") as f:
            f.write("---\n")
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
            f.write("---\n")
            if content:
                f.write(content)

    def get_features_status(self) -> list:
        """Get status of all features"""
        conn = sqlite3.connect(self.db_path)
        try:
            return conn.execute(
                """
            SELECT id, status,
                   (SELECT COUNT(*) FROM checkpoints
                    WHERE feature_id = features.id
                    AND validation_passed = 1) as passing_checkpoints
            FROM features
            ORDER BY created_at
        """
            ).fetchall()
        finally:
            conn.close()

    def checkpoint(self, message: str):
        """Save checkpoint with current state"""
        # Get current state
        validation = self.validator.validate()
        build = self.builder.get_status()

        # Git commit
        try:
            git_hash = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        except Exception:
            git_hash = "no-git"

        # Save checkpoint
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """
            INSERT INTO checkpoints (feature_id, timestamp, validation_passed,
                                    build_passed, git_hash, evidence)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
                (
                    self.session.get_current_feature(),
                    datetime.now().isoformat(),
                    validation["passing"],
                    build["passing"],
                    git_hash,
                    json.dumps({"message": message, "validation": validation, "build": build}),
                ),
            )
            conn.commit()
        finally:
            conn.close()

        # DO NOT write to PROGRESS.md - we're database-first!

    def revert_to_last_checkpoint(self):
        """Revert to last working checkpoint"""
        conn = sqlite3.connect(self.db_path)
        try:
            # CRITICAL FIX: Allow revert with validation-only checkpoints
            # Try to find a checkpoint with both validation AND build passing
            last_good = conn.execute(
                """
            SELECT git_hash, timestamp, validation_passed, build_passed FROM checkpoints
            WHERE validation_passed = 1 AND build_passed = 1
            ORDER BY id DESC LIMIT 1
            """
            ).fetchone()

            # If no perfect checkpoint, try validation-only
            if not last_good:
                last_good = conn.execute(
                    """
                    SELECT git_hash, timestamp, validation_passed, build_passed FROM checkpoints
                    WHERE validation_passed = 1
                    ORDER BY id DESC LIMIT 1
                """
                ).fetchone()

            if not last_good:
                return False, "No checkpoint with passing validation found"

            git_hash, timestamp, val_passed, build_passed = last_good

            # Git revert
            try:
                subprocess.run(["git", "reset", "--hard", git_hash], check=True)
                status = "validation+build" if build_passed else "validation-only"
                return (
                    True,
                    f"Reverted to {status} checkpoint from {timestamp} (Git hash: {git_hash[:7]})",
                )
            except subprocess.CalledProcessError:
                return False, "Git revert failed"
        finally:
            conn.close()
