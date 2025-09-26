"""
Tests for enforcement features
"""

import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, "src")

from rfd.enforcement import WorkflowEnforcer, ScopeDriftDetector, MultiAgentCoordinator
from rfd.rfd import RFD


def test_workflow_enforcement():
    """Test workflow enforcement"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup test RFD
        rfd_dir = Path(tmpdir) / ".rfd"
        rfd_dir.mkdir()

        rfd = RFD()
        rfd.rfd_dir = rfd_dir
        rfd.db_path = rfd_dir / "memory.db"
        rfd._init_database()

        # Add test feature
        import sqlite3

        conn = sqlite3.connect(rfd.db_path)
        conn.execute("INSERT INTO features (id, description, status) VALUES ('test_feature', 'Test', 'pending')")
        conn.commit()
        conn.close()

        # Test enforcement
        enforcer = WorkflowEnforcer(rfd)

        # Start enforcement
        result = enforcer.start_enforcement("test_feature")
        assert result["status"] == "active"
        assert "baseline" in result

        # Test validation
        validation = enforcer.validate_change("src/test.py", "test_feature")
        assert validation["allowed"] == True

        validation = enforcer.validate_change("/etc/passwd", "test_feature")
        assert validation["allowed"] == False
        assert "out of scope" in validation["reason"]

        # Stop enforcement
        result = enforcer.stop_enforcement("test_feature")
        assert result["status"] == "stopped"

        print("✅ Workflow enforcement tests passed")
        return True


def test_drift_detection():
    """Test scope drift detection"""
    with tempfile.TemporaryDirectory() as tmpdir:
        rfd_dir = Path(tmpdir) / ".rfd"
        rfd_dir.mkdir()

        rfd = RFD()
        rfd.rfd_dir = rfd_dir
        rfd.db_path = rfd_dir / "memory.db"
        rfd._init_database()

        # Add feature
        import sqlite3

        conn = sqlite3.connect(rfd.db_path)
        conn.execute("INSERT INTO features (id, description, status) VALUES ('drift_test', 'Test', 'pending')")
        conn.commit()
        conn.close()

        enforcer = WorkflowEnforcer(rfd)
        detector = ScopeDriftDetector(rfd)

        # Start with baseline
        enforcer.start_enforcement("drift_test")

        # Check no drift initially
        drift = detector.detect_drift("drift_test")
        assert drift["drift_detected"] == False

        print("✅ Drift detection tests passed")
        return True


def test_multi_agent_coordination():
    """Test multi-agent coordination"""
    with tempfile.TemporaryDirectory() as tmpdir:
        rfd_dir = Path(tmpdir) / ".rfd"
        rfd_dir.mkdir()

        rfd = RFD()
        rfd.rfd_dir = rfd_dir
        rfd.db_path = rfd_dir / "memory.db"
        rfd._init_database()

        # Ensure tables are created
        coordinator = MultiAgentCoordinator(rfd)
        coordinator._ensure_tables()

        # Register agents
        result = coordinator.register_agent("agent1", ["coding", "testing"])
        assert result["status"] == "registered"

        result = coordinator.register_agent("agent2", ["review", "qa"])
        assert result["status"] == "registered"

        # Create handoff
        handoff = coordinator.create_handoff("agent1", "agent2", "Review code changes", {"files": ["test.py"]})
        assert handoff["status"] == "created"
        assert handoff["handoff_id"] > 0

        # Check pending
        pending = coordinator.get_pending_handoffs("agent2")
        assert len(pending) == 1
        assert pending[0]["task"] == "Review code changes"

        print("✅ Multi-agent coordination tests passed")
        return True


if __name__ == "__main__":
    test_workflow_enforcement()
    test_drift_detection()
    test_multi_agent_coordination()
    print("\n🎉 All enforcement tests passed!")
