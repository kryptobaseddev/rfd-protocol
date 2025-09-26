"""
CLI commands for workflow enforcement
"""

import json
from typing import Optional

import click

from .enforcement import MultiAgentCoordinator, ScopeDriftDetector, WorkflowEnforcer
from .rfd import RFD


@click.group()
def enforce():
    """Real-time workflow enforcement commands"""
    pass


@enforce.command()
@click.argument("feature")
def start(feature: str):
    """Start enforcement for a feature"""
    rfd = RFD()
    enforcer = WorkflowEnforcer(rfd)
    result = enforcer.start_enforcement(feature)

    if result["status"] == "active":
        click.echo(f"✅ Enforcement activated for feature: {feature}")
        click.echo(f"📏 Baseline captured: {result['baseline']['file_count']} files")
    else:
        click.echo(f"❌ {result['message']}")


@enforce.command()
@click.argument("feature")
def stop(feature: str):
    """Stop enforcement for a feature"""
    rfd = RFD()
    enforcer = WorkflowEnforcer(rfd)
    result = enforcer.stop_enforcement(feature)
    click.echo(f"⏹️ Enforcement stopped for: {result['feature']}")


@enforce.command("check-drift")
@click.argument("feature")
def check_drift(feature: str):
    """Check for scope drift"""
    rfd = RFD()
    detector = ScopeDriftDetector(rfd)
    result = detector.detect_drift(feature)

    if result["drift_detected"]:
        click.echo(f"⚠️ Drift detected: {result['reason']}")
        click.echo(f"💡 {result['recommendation']}")
    else:
        click.echo("✅ No drift detected")
        if "metrics" in result:
            click.echo(f"📊 Files: {result['metrics']['original_files']} → {result['metrics']['current_files']}")


@enforce.command("register-agent")
@click.argument("agent_id")
@click.argument("capabilities", nargs=-1)
def register_agent(agent_id: str, capabilities):
    """Register an agent for coordination"""
    rfd = RFD()
    coordinator = MultiAgentCoordinator(rfd)
    result = coordinator.register_agent(agent_id, list(capabilities))
    click.echo(f"✅ Agent registered: {result['agent_id']}")


@enforce.command()
@click.argument("from_agent")
@click.argument("to_agent")
@click.argument("task")
@click.option("--context", "-c", help="JSON context for handoff")
def handoff(from_agent: str, to_agent: str, task: str, context: Optional[str]):
    """Create handoff between agents"""
    rfd = RFD()
    coordinator = MultiAgentCoordinator(rfd)

    ctx = json.loads(context) if context else {}
    result = coordinator.create_handoff(from_agent, to_agent, task, ctx)

    click.echo(f"✅ Handoff created: #{result['handoff_id']}")
    click.echo(f"   {from_agent} → {to_agent}: {task}")


@enforce.command("pending")
@click.argument("agent_id")
def pending(agent_id: str):
    """Show pending handoffs for an agent"""
    rfd = RFD()
    coordinator = MultiAgentCoordinator(rfd)
    handoffs = coordinator.get_pending_handoffs(agent_id)

    if handoffs:
        click.echo(f"📥 Pending handoffs for {agent_id}:")
        for h in handoffs:
            click.echo(f"  #{h['id']}: {h['task']} (from {h['from']})")
    else:
        click.echo(f"No pending handoffs for {agent_id}")


@enforce.command("validate-commit")
def validate_commit():
    """Validate commit against specs (for git hooks)"""
    import subprocess
    import sys

    # Get staged files
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)

    if result.returncode != 0:
        click.echo("❌ Failed to get staged files")
        sys.exit(1)

    staged_files = result.stdout.strip().split("\n") if result.stdout.strip() else []

    # Basic validation - check for common issues
    issues = []

    for file in staged_files:
        # Check for test files if src files are modified
        if file.startswith("src/") and file.endswith(".py"):
            test_file = file.replace("src/", "tests/test_").replace(".py", ".py")
            if test_file not in staged_files and not any(t.startswith("tests/") for t in staged_files):
                issues.append(f"⚠️ {file} modified but no tests included")

    if issues:
        click.echo("⚠️ Commit validation warnings:")
        for issue in issues:
            click.echo(f"  {issue}")
        # Don't block, just warn

    click.echo("✅ Commit validated")
    sys.exit(0)
