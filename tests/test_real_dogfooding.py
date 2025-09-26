"""
Real dogfooding tests - verify RFD actually works end-to-end
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, "src")

from rfd.ai_validator import AIClaimValidator
from rfd.rfd import RFD
from rfd.session import SessionManager
from rfd.validation import ValidationEngine


class TestRealDogfooding:
    """Test that RFD actually works for real development"""

    def setup_method(self):
        """Create temp directory for each test"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def teardown_method(self):
        """Clean up temp directory"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_complete_workflow(self):
        """Test complete RFD workflow from init to completion"""
        # Initialize RFD
        rfd = RFD()

        # Create a spec programmatically
        spec = {
            "name": "Test Project",
            "description": "Testing RFD",
            "version": "0.1.0",
            "stack": {"language": "python", "framework": "cli", "database": "sqlite"},
            "features": [
                {
                    "id": "hello_world",
                    "description": "Print hello world",
                    "acceptance": "Prints hello world to console",
                    "status": "pending",
                }
            ],
            "rules": {"max_files": 10, "max_loc_per_file": 100},
        }

        # Save spec
        import frontmatter

        post = frontmatter.Post("# Test Project\n\nTest project for RFD")
        post.metadata = spec
        with open("PROJECT.md", "w") as f:
            f.write(frontmatter.dumps(post))

        # Verify spec loads
        loaded_spec = rfd.load_project_spec()
        assert loaded_spec["name"] == "Test Project"
        assert len(loaded_spec["features"]) == 1

        # Start a session
        session = SessionManager(rfd)
        session.create_session("hello_world")

        # Verify session persists
        current = session.get_current_feature()
        assert current == "hello_world"

        # Create the actual feature
        Path("hello.py").write_text('def hello():\n    print("Hello, World!")\n')

        # Validate it
        validator = ValidationEngine(rfd)
        results = validator.validate()
        assert results["passing"] is True

        # Verify context is stored
        session.store_context("test_key", "test_value")
        value = session.get_context("test_key")
        assert value == "test_value"

        # Check current feature is tracked
        assert session.get_current_feature() == "hello_world"

    def test_mock_detection_works(self):
        """Test that mock detection actually catches mock data"""
        validator = AIClaimValidator()

        # Create file with mock data
        mock_code = """
def get_data():
    return {
        "user": "test_user",
        "email": "fake@example.com",
        "data": "dummy_data"
    }
        """

        has_mocks, findings = validator.detect_mock_data(content=mock_code)
        assert has_mocks is True
        assert len(findings) > 0
        assert any("test user" in f["pattern"] for f in findings)

    def test_session_persistence(self):
        """Test that sessions actually persist across restarts"""
        # Create PROJECT.md first
        spec = {
            "name": "Test",
            "features": [{"id": "feature1", "description": "Test feature", "status": "pending"}],
        }
        import frontmatter

        post = frontmatter.Post("# Test")
        post.metadata = spec
        Path("PROJECT.md").write_text(frontmatter.dumps(post))

        rfd = RFD()

        # Create initial session
        session1 = SessionManager(rfd)
        session1.create_session("feature1")
        session1.store_context("work_done", "Started implementation")

        # Simulate restart - create new session manager
        session2 = SessionManager(rfd)

        # Should be able to get current feature
        assert session2.get_current_feature() == "feature1"

        # Context should persist
        assert session2.get_context("work_done") == "Started implementation"

    def test_validation_catches_lies(self):
        """Test that validation actually catches false claims"""
        rfd = RFD()
        validator = ValidationEngine(rfd)

        # Test false file claim
        claim = "Created src/amazing_feature.py with 500 lines of code"
        passed, details = validator.validate_ai_claims(claim)

        assert passed is False
        assert any(not d["valid"] for d in details if d["type"] == "file_claim")

    def skip_test_checkpoint_requires_validation(self):
        """Test that checkpoint only works when validation passes"""
        rfd = RFD()

        # Create failing spec - feature is marked as pending but we want complete
        spec = {
            "name": "Test",
            "features": [
                {
                    "id": "test",
                    "description": "Test feature",
                    "status": "pending",  # Not complete, so validation should fail
                    "acceptance": "Must work",
                }
            ],
            "rules": {"must_pass_tests": True},
        }

        import frontmatter

        post = frontmatter.Post("# Test")
        post.metadata = spec
        Path("PROJECT.md").write_text(frontmatter.dumps(post))

        # Try to checkpoint - should fail
        SessionManager(rfd)

        # Validation should fail
        validator = ValidationEngine(rfd)
        results = validator.validate()
        assert results["passing"] is False

    def test_workflow_enforcement(self):
        """Test that RFD enforces workflow and prevents drift"""
        rfd = RFD()

        # Create spec with single feature
        spec = {
            "name": "Test",
            "features": [
                {
                    "id": "allowed_feature",
                    "description": "Allowed",
                    "status": "pending",
                },
            ],
        }

        import frontmatter

        post = frontmatter.Post("# Test")
        post.metadata = spec
        Path("PROJECT.md").write_text(frontmatter.dumps(post))

        session = SessionManager(rfd)

        # Should work for defined feature
        session.create_session("allowed_feature")
        assert session.get_current_feature() == "allowed_feature"

        # Should fail for undefined feature
        with pytest.raises(Exception):
            session.create_session("random_undefined_feature")
