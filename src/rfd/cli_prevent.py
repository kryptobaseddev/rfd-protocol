#!/usr/bin/env python3
"""Prevention CLI commands for RFD."""

import json
import sys
from pathlib import Path

import click

from .prevention import HallucinationPrevention, ScopeDriftPrevention, WorkflowEnforcement


@click.group()
def prevent():
    """Real-time prevention mechanisms for code quality."""
    pass


@prevent.command()
@click.argument("file_path")
@click.argument("code", required=False)
def validate(file_path, code):
    """Validate code before writing to prevent hallucinations."""
    hp = HallucinationPrevention()

    if not code:
        # First try to read the file if it exists
        file = Path(file_path)
        if file.exists() and file.is_file():
            code = file.read_text()
        else:
            # Otherwise read from stdin
            code = sys.stdin.read()

    valid, violations = hp.validate_code_before_write(file_path, code)

    if not valid:
        click.echo("❌ Code validation failed:")
        for violation in violations:
            click.echo(f"  - {violation}")
        sys.exit(1)
    else:
        click.echo("✅ Code validation passed")


@prevent.command()
def check_scope():
    """Check for scope drift in current changes."""
    sdp = ScopeDriftPrevention()

    valid, violations = sdp.check_current_changes()

    if not valid:
        click.echo("❌ Scope drift detected:")
        for violation in violations:
            click.echo(f"  - {violation}")
        sys.exit(1)
    else:
        click.echo("✅ No scope drift detected")


@prevent.command()
@click.argument("workflow_id", required=False)
def validate_commit(workflow_id):
    """Validate commit against workflow rules."""
    we = WorkflowEnforcement()

    if not workflow_id and Path(".rfd/workflow.lock").exists():
        workflow_id = Path(".rfd/workflow.lock").read_text().strip()

    if not workflow_id:
        click.echo("No active workflow")
        return

    valid, violations = we.validate_workflow_compliance(workflow_id)

    if not valid:
        click.echo(f"❌ Workflow {workflow_id} violations:")
        for violation in violations:
            click.echo(f"  - {violation}")
        sys.exit(1)
    else:
        click.echo(f"✅ Workflow {workflow_id} compliant")


@prevent.command()
def stats():
    """Show prevention statistics."""
    hp = HallucinationPrevention()
    stats = hp.get_prevention_stats()

    click.echo("=== Prevention Statistics ===")
    click.echo(f"Total validations: {stats['total_validations']}")
    click.echo(f"Violations prevented: {stats['violations_prevented']}")

    if stats.get("recent_violations"):
        click.echo("\nRecent violations prevented:")
        for v in stats["recent_violations"][-5:]:
            click.echo(f"  - {v}")


@prevent.command()
@click.argument("feature_id")
def lock_workflow(feature_id):
    """Acquire exclusive lock for a workflow/feature."""
    from .prevention import WorkflowLockManager
    wlm = WorkflowLockManager()
    
    if wlm.acquire_lock(feature_id):
        click.echo(f"✅ Acquired lock for {feature_id}")
    else:
        current = wlm.get_current_lock()
        click.echo(f"❌ Lock failed - held by {current}")
        sys.exit(1)


@prevent.command()
@click.argument("feature_id")
def unlock_workflow(feature_id):
    """Release lock for a workflow/feature."""
    from .prevention import WorkflowLockManager
    wlm = WorkflowLockManager()
    
    if wlm.release_lock(feature_id):
        click.echo(f"✅ Released lock for {feature_id}")
    else:
        current = wlm.get_current_lock()
        click.echo(f"❌ Cannot release - held by {current}")
        sys.exit(1)


@prevent.command()
def workflow_status():
    """Show current workflow lock status."""
    from .prevention import WorkflowLockManager
    wlm = WorkflowLockManager()
    
    current = wlm.get_current_lock()
    if current:
        click.echo(f"🔒 Locked by: {current}")
    else:
        click.echo("🔓 No active lock")


@prevent.command()
def install_hooks():
    """Install git hooks for real-time prevention."""
    hooks_dir = Path(".git/hooks")
    if not hooks_dir.exists():
        click.echo("❌ Not a git repository")
        sys.exit(1)

    # No need for validate-commit script since we use rfd commands directly

    # Update pre-commit hook
    pre_commit = hooks_dir / "pre-commit"
    pre_commit.write_text(
        """#!/bin/bash
# RFD Workflow Enforcement Hook

# Check if we're in an RFD workflow
if [ -f .rfd/workflow.lock ]; then
    workflow_id=$(cat .rfd/workflow.lock)
    
    # Validate changes against workflow spec
    rfd prevent validate-commit $workflow_id
    if [ $? -ne 0 ]; then
        echo "❌ Commit blocked: Workflow violation detected"
        echo "Run 'rfd workflow status $workflow_id' for details"
        exit 1
    fi
fi

# Check for scope drift
rfd prevent check-scope
if [ $? -ne 0 ]; then
    echo "❌ Commit blocked: Scope drift detected"
    echo "Run 'rfd scope check' for details"
    exit 1
fi

exit 0
"""
    )
    pre_commit.chmod(0o755)

    # Update pre-push hook
    pre_push = hooks_dir / "pre-push"
    pre_push.write_text(
        """#!/bin/bash
# RFD Feature Validation Hook

# Run full validation before push
rfd validate
if [ $? -ne 0 ]; then
    echo "❌ Push blocked: Validation failed"
    exit 1
fi

exit 0
"""
    )
    pre_push.chmod(0o755)

    click.echo("✅ Git hooks installed:")
    click.echo("  - pre-commit: Workflow and scope validation")
    click.echo("  - pre-push: Full feature validation")
