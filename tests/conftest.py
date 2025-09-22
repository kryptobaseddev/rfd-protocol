"""
Shared pytest fixtures for RFD test suite.

This file provides common fixtures used across all test categories:
- unit tests (fast, isolated)
- integration tests (component interaction)
- system tests (end-to-end workflows)
"""

import pytest
import tempfile
import shutil
import sqlite3
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rfd.rfd import RFD
from rfd.validation import ValidationEngine
from rfd.session import SessionManager
from rfd.build import BuildEngine
from rfd.spec import SpecEngine


@pytest.fixture(scope="session")
def project_root():
    """Path to project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="function")
def temp_project():
    """Temporary directory for test projects."""
    temp_dir = tempfile.mkdtemp(prefix="rfd_test_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def temp_db():
    """Temporary SQLite database for testing."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield db_path
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture(scope="function")
def mock_rfd():
    """Mock RFD instance for testing."""
    mock = Mock(spec=RFD)
    mock.project_root = Path("/tmp/test_project")
    mock.config = {"debug": True}
    return mock


@pytest.fixture(scope="function")
def validation_engine(temp_db):
    """ValidationEngine instance with temporary database."""
    mock_rfd = Mock()
    mock_rfd.project_root = Path("/tmp/test")
    mock_rfd.config = {}
    
    # Create temporary database
    conn = sqlite3.connect(temp_db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS checkpoints (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            feature TEXT,
            status TEXT,
            details TEXT
        )
    """)
    conn.close()
    
    ve = ValidationEngine(mock_rfd)
    ve.db_path = temp_db
    return ve


@pytest.fixture(scope="function")
def session_manager(temp_db):
    """SessionManager instance with temporary database."""
    mock_rfd = Mock()
    mock_rfd.project_root = Path("/tmp/test")
    
    sm = SessionManager(mock_rfd)
    sm.db_path = temp_db
    sm._init_database()
    return sm


@pytest.fixture(scope="function")
def build_engine():
    """BuildEngine instance for testing."""
    mock_rfd = Mock()
    mock_rfd.project_root = Path("/tmp/test")
    mock_rfd.config = {}
    return BuildEngine(mock_rfd)


@pytest.fixture(scope="function")
def spec_engine():
    """SpecEngine instance for testing."""
    mock_rfd = Mock()
    mock_rfd.project_root = Path("/tmp/test")
    return SpecEngine(mock_rfd)


@pytest.fixture(scope="function")
def sample_python_project(temp_project):
    """Create a sample Python project for testing."""
    project_dir = temp_project / "sample_python"
    project_dir.mkdir()
    
    # Create sample files
    (project_dir / "app.py").write_text("""
def main():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    main()
""")
    
    (project_dir / "requirements.txt").write_text("flask>=2.0.0\nrequests>=2.28.0")
    
    (project_dir / "PROJECT.md").write_text("""
# Sample Python Project

## Features
- [ ] Feature 1: Main application
- [ ] Feature 2: Web interface
- [ ] Feature 3: Database integration
""")
    
    return project_dir


@pytest.fixture(scope="function")
def sample_javascript_project(temp_project):
    """Create a sample JavaScript project for testing."""
    project_dir = temp_project / "sample_js"
    project_dir.mkdir()
    
    # Create sample files
    (project_dir / "index.js").write_text("""
function main() {
    console.log("Hello, World!");
    return true;
}

module.exports = { main };
""")
    
    (project_dir / "package.json").write_text("""{
  "name": "sample-js-project",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "express": "^4.18.0"
  }
}""")
    
    return project_dir


@pytest.fixture(scope="function")
def mock_requests():
    """Mock requests module for HTTP testing."""
    mock = MagicMock()
    mock.get.return_value.status_code = 200
    mock.get.return_value.json.return_value = {"status": "ok"}
    mock.post.return_value.status_code = 200
    mock.post.return_value.json.return_value = {"result": "success"}
    return mock


@pytest.fixture(scope="function")
def mock_subprocess():
    """Mock subprocess for command execution testing."""
    mock = MagicMock()
    mock.run.return_value.returncode = 0
    mock.run.return_value.stdout = "Success"
    mock.run.return_value.stderr = ""
    return mock


# Pytest markers configuration
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "system: System/E2E tests")
    config.addinivalue_line("markers", "smoke: Smoke tests")
    config.addinivalue_line("markers", "regression: Regression tests")


# Test data fixtures
@pytest.fixture(scope="session")
def sample_ai_claims():
    """Sample AI claims for hallucination testing."""
    return {
        "true_claims": [
            "Created tests/conftest.py with pytest fixtures",
            "Modified pyproject.toml to add ruff configuration",
            "Added function test_basic_functionality() to existing file"
        ],
        "false_claims": [
            "Created /nonexistent/fake_file.py with magic_function()",
            "Modified nonexistent_file.py to add error_handling()",
            "Added function that_does_not_exist() to real_file.py"
        ],
        "complex_claims": [
            "Created multiple files: src/new.py, tests/test_new.py, docs/new.md",
            "Refactored entire codebase to use async/await patterns",
            "Added comprehensive error handling throughout the application"
        ]
    }


@pytest.fixture(scope="session")
def sample_project_specs():
    """Sample project specifications for testing."""
    return {
        "valid_spec": """---
title: Test Project
features:
  - name: Authentication
    status: planned
  - name: Dashboard
    status: in_progress
  - name: API
    status: completed
---

# Test Project

This is a test project specification.
""",
        "invalid_spec": "This is not a valid specification",
        "malformed_yaml": """---
title: Test
features:
  - name: Feature 1
    status: invalid_status
  - invalid_feature_format
---
"""
    }