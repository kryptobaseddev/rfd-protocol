"""
Database utilities for RFD with WAL mode support
Ensures consistent SQLite configuration across all connections
"""

import sqlite3
from pathlib import Path


def get_db_connection(db_path: str | Path, timeout: float = 30.0) -> sqlite3.Connection:
    """
    Create a SQLite connection with WAL mode and optimal settings.

    WAL (Write-Ahead Logging) benefits:
    - Better concurrency - readers don't block writers
    - Better performance for write-heavy workloads
    - More robust crash recovery
    - Consistent memory context across sessions

    Args:
        db_path: Path to the SQLite database
        timeout: Connection timeout in seconds

    Returns:
        Configured SQLite connection
    """
    conn = sqlite3.connect(str(db_path), timeout=timeout)

    # Enable WAL mode for better concurrency and performance
    conn.execute("PRAGMA journal_mode=WAL")

    # Optimize for performance
    conn.execute("PRAGMA synchronous=NORMAL")  # Good balance of safety and speed
    conn.execute("PRAGMA cache_size=10000")  # Increase cache size (pages)
    conn.execute("PRAGMA temp_store=MEMORY")  # Use memory for temp tables

    # Enable foreign keys for referential integrity
    conn.execute("PRAGMA foreign_keys=ON")

    # Row factory for dict-like access
    conn.row_factory = sqlite3.Row

    return conn


def init_database(db_path: str | Path) -> None:
    """
    Initialize the RFD database with all required tables.
    This consolidates all table creation in one place.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Core session management
    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            feature_id TEXT,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            status TEXT DEFAULT 'active'
        );

        CREATE TABLE IF NOT EXISTS features (
            id TEXT PRIMARY KEY,
            description TEXT,
            acceptance TEXT,
            status TEXT DEFAULT 'pending',
            priority TEXT,
            started_at TEXT,
            completed_at TEXT,
            estimated_hours REAL,
            actual_hours REAL
        );

        CREATE TABLE IF NOT EXISTS checkpoints (
            id INTEGER PRIMARY KEY,
            session_id INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            message TEXT,
            validation_passed BOOLEAN,
            build_passed BOOLEAN,
            git_hash TEXT,
            feature_id TEXT
        );

        CREATE TABLE IF NOT EXISTS context (
            id INTEGER PRIMARY KEY,
            session_id INTEGER,
            key TEXT,
            value TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        -- Spec-kit style tables
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            feature_id TEXT,
            phase_id TEXT,
            description TEXT,
            status TEXT DEFAULT 'pending',
            can_parallel BOOLEAN DEFAULT 0,
            order_index INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT,
            FOREIGN KEY (feature_id) REFERENCES features (id)
        );

        CREATE TABLE IF NOT EXISTS project_phases (
            id TEXT PRIMARY KEY,
            name TEXT,
            description TEXT,
            status TEXT DEFAULT 'pending',
            order_index INTEGER,
            started_at TEXT,
            completed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS workflow_state (
            id INTEGER PRIMARY KEY,
            feature_id TEXT,
            current_state TEXT,
            locked_by TEXT,
            locked_at TEXT,
            data JSON,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (feature_id) REFERENCES features (id)
        );

        CREATE TABLE IF NOT EXISTS workflow_checkpoints (
            id INTEGER PRIMARY KEY,
            workflow_id INTEGER,
            state TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            data JSON,
            FOREIGN KEY (workflow_id) REFERENCES workflow_state (id)
        );

        -- Hallucination and drift tracking
        CREATE TABLE IF NOT EXISTS hallucination_log (
            id INTEGER PRIMARY KEY,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            claim TEXT,
            actual TEXT,
            detected_by TEXT,
            severity TEXT
        );

        CREATE TABLE IF NOT EXISTS drift_log (
            id INTEGER PRIMARY KEY,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            expected TEXT,
            actual TEXT,
            component TEXT,
            resolved BOOLEAN DEFAULT 0
        );

        -- Query resolution for spec ambiguities
        CREATE TABLE IF NOT EXISTS workflow_queries (
            id INTEGER PRIMARY KEY,
            workflow_id INTEGER,
            query TEXT,
            response TEXT,
            resolved_at TEXT,
            FOREIGN KEY (workflow_id) REFERENCES workflow_state (id)
        );

        -- Constitution storage (immutable principles)
        CREATE TABLE IF NOT EXISTS constitution (
            id INTEGER PRIMARY KEY,
            principle TEXT UNIQUE,
            category TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            immutable BOOLEAN DEFAULT 1
        );

        -- API contract storage
        CREATE TABLE IF NOT EXISTS api_contracts (
            id INTEGER PRIMARY KEY,
            feature_id TEXT,
            endpoint TEXT,
            method TEXT,
            description TEXT,
            request_schema JSON,
            response_schema JSON,
            auth_required BOOLEAN,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (feature_id) REFERENCES features (id)
        );

        -- Create indexes for better performance
        CREATE INDEX IF NOT EXISTS idx_sessions_feature ON sessions(feature_id);
        CREATE INDEX IF NOT EXISTS idx_tasks_feature ON tasks(feature_id);
        CREATE INDEX IF NOT EXISTS idx_workflow_state_feature ON workflow_state(feature_id);
        CREATE INDEX IF NOT EXISTS idx_api_contracts_feature ON api_contracts(feature_id);
    """
    )

    conn.commit()
    conn.close()


def migrate_to_wal(db_path: str | Path) -> bool:
    """
    Migrate existing database to WAL mode.

    Returns:
        True if migration successful or already in WAL mode
    """
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check current journal mode
        result = cursor.execute("PRAGMA journal_mode").fetchone()
        current_mode = result[0] if result else "delete"

        if current_mode.lower() == "wal":
            # Already in WAL mode, no need to print
            conn.close()
            return True

        # Switch to WAL mode
        cursor.execute("PRAGMA journal_mode=WAL")
        result = cursor.execute("PRAGMA journal_mode").fetchone()
        new_mode = result[0] if result else "unknown"

        if new_mode.lower() == "wal":
            print("Successfully migrated database to WAL mode")
            conn.commit()
            conn.close()
            return True
        else:
            print(f"Failed to migrate to WAL mode, still in {new_mode} mode")
            conn.close()
            return False

    except Exception as e:
        print(f"Error migrating to WAL mode: {e}")
        return False


def verify_database_integrity(db_path: str | Path) -> bool:
    """
    Verify database integrity and structure.

    Returns:
        True if database is healthy
    """
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()

        # Check integrity
        result = cursor.execute("PRAGMA integrity_check").fetchone()
        if result[0] != "ok":
            print(f"Database integrity check failed: {result[0]}")
            return False

        # Verify all required tables exist
        required_tables = [
            "sessions",
            "features",
            "checkpoints",
            "context",
            "tasks",
            "project_phases",
            "workflow_state",
            "hallucination_log",
            "drift_log",
            "constitution",
            "api_contracts",
        ]

        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """
        )
        existing_tables = {row[0] for row in cursor.fetchall()}

        missing_tables = set(required_tables) - existing_tables
        if missing_tables:
            print(f"Missing tables: {missing_tables}")
            return False

        # Check WAL mode
        result = cursor.execute("PRAGMA journal_mode").fetchone()
        if result[0].lower() != "wal":
            print(f"Database not in WAL mode: {result[0]}")
            return False

        conn.close()
        return True

    except Exception as e:
        print(f"Database verification error: {e}")
        return False
