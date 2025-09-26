"""
Database migrations for QA cycles feature
"""

import sqlite3
from pathlib import Path


def create_qa_tables(db_path: Path):
    """Create tables for QA cycles and review results"""
    conn = sqlite3.connect(db_path)
    
    # Create qa_cycles table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS qa_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_id TEXT NOT NULL,
            cycle_number INTEGER NOT NULL,
            status TEXT NOT NULL,
            started_at DATETIME NOT NULL,
            completed_at DATETIME,
            FOREIGN KEY (feature_id) REFERENCES features(id)
        )
    """)
    
    # Create review_results table
    conn.execute("""
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
    """)
    
    # Create agent_handoffs table if it doesn't exist
    conn.execute("""
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
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ QA cycle tables created successfully")


if __name__ == "__main__":
    # Run migration for current project
    from rfd import RFD
    rfd = RFD()
    create_qa_tables(rfd.db_path)