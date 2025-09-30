#!/usr/bin/env python3
"""
Test automated QA cycles implementation
"""

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.rfd import RFD
from src.rfd.auto_handoff import AutoHandoff
from src.rfd.enforcement import EnforcementEngine
from src.rfd.migration import RFDMigration
from src.rfd.workflow_engine import WorkflowEngine


class TestQACycles(unittest.TestCase):
    """Test QA cycle functionality"""

    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = Path.cwd()
        import os

        os.chdir(self.test_dir)

        # Initialize RFD
        self.rfd = RFD()

        # Create QA tables
        migrator = RFDMigration()
        migrator.create_qa_tables(self.rfd.db_path)

        # Add test feature
        conn = sqlite3.connect(self.rfd.db_path)
        conn.execute(
            """
            INSERT INTO features (id, description, status, created_at)
            VALUES ('test_qa_feature', 'Test feature for QA cycles', 'building', datetime('now'))
        """
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        """Clean up test environment"""
        import os

        os.chdir(self.old_cwd)

    def test_review_trigger(self):
        """Test review trigger functionality"""
        enforcer = EnforcementEngine(self.rfd)

        # Trigger pre-commit review
        results = enforcer.trigger_review("pre_commit", "test_qa_feature")

        self.assertIsNotNone(results)
        self.assertIn("cycle_id", results)
        self.assertIn("trigger", results)
        self.assertIn("passed", results)
        self.assertIn("issues", results)
        self.assertIn("suggestions", results)
        self.assertEqual(results["trigger"], "pre_commit")

    def test_agent_handoff(self):
        """Test agent handoff creation and retrieval"""
        handoff = AutoHandoff(self.rfd)

        # Create handoff
        handoff_id = handoff.handoff(
            from_agent="review",
            to_agent="fix",
            task="Fix validation issues",
            context={"issues": ["Test issue 1", "Test issue 2"]},
        )

        self.assertIsNotNone(handoff_id)
        self.assertGreater(handoff_id, 0)

        # Get pending handoffs
        pending = handoff.get_pending_handoffs("fix")
        self.assertIsInstance(pending, list)

        # Find our handoff
        our_handoff = next((h for h in pending if h["id"] == handoff_id), None)
        self.assertIsNotNone(our_handoff)
        self.assertEqual(our_handoff["from"], "review")
        self.assertEqual(our_handoff["task"], "Fix validation issues")
        self.assertIn("issues", our_handoff["context"])

        # Complete handoff
        handoff.complete_handoff(handoff_id, "completed")

        # Should no longer be pending
        pending = handoff.get_pending_handoffs("fix")
        our_handoff = next((h for h in pending if h["id"] == handoff_id), None)
        self.assertIsNone(our_handoff)

    def test_review_status(self):
        """Test getting review status"""
        enforcer = EnforcementEngine(self.rfd)

        # Initially no reviews
        status = enforcer.get_review_status("test_qa_feature")
        self.assertEqual(status["status"], "no_reviews")
        self.assertEqual(status["cycles"], 0)

        # Trigger a review
        enforcer.trigger_review("pre_commit", "test_qa_feature")

        # Now should have review status
        status = enforcer.get_review_status("test_qa_feature")
        self.assertNotEqual(status["status"], "no_reviews")
        self.assertIn("cycle_number", status)
        self.assertIn("reviews", status)

    def test_qa_cycle_workflow(self):
        """Test complete QA cycle workflow"""
        workflow = WorkflowEngine(self.rfd)

        # Run QA cycle with max 2 iterations
        results = workflow.run_qa_cycle("test_qa_feature", max_iterations=2)

        self.assertIsNotNone(results)
        self.assertEqual(results["feature_id"], "test_qa_feature")
        self.assertIn("cycles", results)
        self.assertIn("final_status", results)
        self.assertIn("reviews", results)
        self.assertGreater(results["cycles"], 0)
        self.assertLessEqual(results["cycles"], 2)

    def test_qa_metrics(self):
        """Test QA metrics retrieval"""
        workflow = WorkflowEngine(self.rfd)
        enforcer = EnforcementEngine(self.rfd)

        # Run some reviews
        enforcer.trigger_review("pre_commit", "test_qa_feature")
        enforcer.trigger_review("post_build", "test_qa_feature")

        # Get metrics
        metrics = workflow.get_qa_metrics("test_qa_feature")

        self.assertIsNotNone(metrics)
        self.assertEqual(metrics["feature_id"], "test_qa_feature")
        self.assertIn("current_status", metrics)
        self.assertIn("metrics", metrics)

        metrics_data = metrics["metrics"]
        self.assertIn("total_cycles", metrics_data)
        self.assertIn("passed_cycles", metrics_data)
        self.assertIn("failed_cycles", metrics_data)
        self.assertIn("success_rate", metrics_data)
        self.assertIn("avg_duration_minutes", metrics_data)

    def test_acceptance_criteria_review_triggers(self):
        """Test: Automated review triggers work"""
        enforcer = EnforcementEngine(self.rfd)

        # Test pre-commit trigger
        pre_commit = enforcer.trigger_review("pre_commit", "test_qa_feature")
        self.assertIsNotNone(pre_commit)
        self.assertEqual(pre_commit["trigger"], "pre_commit")

        # Test post-build trigger
        post_build = enforcer.trigger_review("post_build", "test_qa_feature")
        self.assertIsNotNone(post_build)
        self.assertEqual(post_build["trigger"], "post_build")

        print("✅ Acceptance Criteria 1: Automated review triggers work")

    def test_acceptance_criteria_qa_loops(self):
        """Test: Code-QA-Fix loops are enforced"""
        workflow = WorkflowEngine(self.rfd)

        # Run QA cycle - it should iterate
        results = workflow.run_qa_cycle("test_qa_feature", max_iterations=3)

        # Verify loops occurred
        self.assertGreater(results["cycles"], 0)
        self.assertIsInstance(results["reviews"], list)

        # Each cycle should have review results
        for review in results["reviews"]:
            self.assertIn("passed", review)
            self.assertIn("issues", review)

        print("✅ Acceptance Criteria 2: Code-QA-Fix loops are enforced")

    def test_acceptance_criteria_agent_handoffs(self):
        """Test: Review handoffs between agents functional"""
        handoff = AutoHandoff(self.rfd)

        # Test handoff from review to fix
        handoff_id = handoff.handoff(
            from_agent="review", to_agent="fix", task="Fix review issues", context={"issues": ["Issue 1"]}
        )
        self.assertGreater(handoff_id, 0)

        # Test handoff from qa to fix
        handoff_id2 = handoff.handoff(
            from_agent="qa", to_agent="fix", task="Fix QA issues", context={"issues": ["QA Issue"]}
        )
        self.assertGreater(handoff_id2, 0)

        # Verify context is preserved
        pending = handoff.get_pending_handoffs("fix")
        self.assertGreater(len(pending), 0)

        for h in pending:
            self.assertIn("context", h)
            self.assertIsInstance(h["context"], dict)

        print("✅ Acceptance Criteria 3: Review handoffs between agents functional")


if __name__ == "__main__":
    unittest.main()
