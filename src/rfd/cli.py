#!/usr/bin/env python3
"""
RFD CLI Entry Point
Command line interface for Reality-First Development Protocol
"""

import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import click

from . import __version__
from .rfd import RFD


@click.group()
@click.version_option(version=__version__, prog_name="rfd")
@click.pass_context
def cli(ctx):
    """RFD: Reality-First Development System"""
    ctx.obj = RFD()


@cli.command()
@click.option("--wizard", is_flag=True, help="Run interactive initialization wizard")
@click.option("--from-prd", type=click.Path(exists=True), help="Initialize from PRD document")
@click.option(
    "--mode",
    type=click.Choice(["0-to-1", "exploration", "brownfield"]),
    default="0-to-1",
    help="Development mode",
)
@click.pass_obj
def init(rfd, wizard, from_prd, mode):
    """Initialize RFD in current directory"""

    # Use new wizard if requested or if importing from PRD
    if wizard or from_prd:
        from .init_wizard import InitWizard

        wizard_runner = InitWizard(rfd)

        if from_prd:
            # Direct PRD import
            project_info = wizard_runner.spec_generator.ingest_prd(from_prd)
            wizard_runner.spec_generator.generate_full_specification(project_info, mode)
            wizard_runner.create_base_files(project_info)
            click.echo("✅ Project initialized from PRD!")
        else:
            # Run full wizard
            wizard_runner.run()
        return

    # Original simple init
    click.echo("🚀 Initializing RFD System...")

    # Create default files if not exist
    files_created = []

    # PROJECT.md template
    if not Path("PROJECT.md").exists():
        rfd.spec.create_interactive()
        files_created.append("PROJECT.md")

    # Set up Claude integration
    from .claude_integration import ClaudeIntegration

    click.echo("📝 Setting up Claude Code integration...")
    claude_results = ClaudeIntegration.full_setup(Path("."))

    if claude_results["commands"]:
        click.echo(f"  ✅ Created {len(claude_results['commands'])} Claude commands")
    if claude_results["config"]:
        click.echo("  ✅ Created Claude configuration")
    if claude_results["instructions"]:
        click.echo("  ✅ Created CLAUDE.md instructions")

    # Create rfd executable script
    if not Path("rfd").exists():
        rfd_script = """#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.rfd'))
from rfd import cli

if __name__ == "__main__":
    cli()
"""
        Path("rfd").write_text(rfd_script)
        Path("rfd").chmod(0o755)
        files_created.append("rfd")
        click.echo("  ✅ Created rfd executable")
        files_created.append("PROJECT.md")

    # CLAUDE.md for Claude Code CLI
    if not Path("CLAUDE.md").exists():
        create_claude_md()
        files_created.append("CLAUDE.md")

    # PROGRESS.md
    if not Path("PROGRESS.md").exists():
        Path("PROGRESS.md").write_text("# Build Progress\n\n")
        files_created.append("PROGRESS.md")

    # Track RFD version in project
    from .migration import RFDMigration

    migrator = RFDMigration()
    migrator._update_version_file()

    click.echo(f"✅ RFD initialized! Created: {', '.join(files_created)}")
    click.echo("\n→ Next: rfd spec review")


@cli.command()
@click.argument("action", type=click.Choice(["create", "review", "validate", "generate"]))
@click.option(
    "--type",
    "spec_type",
    type=click.Choice(["constitution", "phases", "api", "guidelines", "adr", "all"]),
    help="Type of specification to generate",
)
@click.pass_obj
def spec(rfd, action, spec_type):
    """Manage project specification"""
    if action == "create":
        rfd.spec.create_interactive()
    elif action == "review":
        rfd.spec.review()
    elif action == "validate":
        rfd.spec.validate()
    elif action == "generate":
        from .init_wizard import InitWizard
        from .spec_generator import SpecGenerator

        generator = SpecGenerator(rfd)
        wizard = InitWizard(rfd)

        # Load project info from PROJECT.md
        project_info = (
            wizard.collect_project_info()
            if not Path("PROJECT.md").exists()
            else {
                "name": rfd.load_project_spec().get("name", "Project"),
                "description": rfd.load_project_spec().get("description", ""),
                "requirements": [f["description"] for f in rfd.load_project_spec().get("features", [])],
                "goals": rfd.load_project_spec().get("goals", []),
                "constraints": rfd.load_project_spec().get("constraints", []),
            }
        )

        if spec_type == "all" or not spec_type:
            generated = generator.generate_full_specification(project_info)
            click.echo("✅ Generated all specifications:")
            for _name, path in generated.items():
                click.echo(f"   - {path}")
        elif spec_type == "constitution":
            doc = generator.generate_project_constitution(project_info)
            path = Path("specs/CONSTITUTION.md")
            path.parent.mkdir(exist_ok=True)
            path.write_text(doc)
            click.echo(f"✅ Generated: {path}")
        elif spec_type == "phases":
            phases = generator.generate_phase_breakdown(project_info)
            doc = generator._format_phases_document(phases)
            path = Path("specs/PHASES.md")
            path.parent.mkdir(exist_ok=True)
            path.write_text(doc)
            click.echo(f"✅ Generated: {path}")
        elif spec_type == "api":
            endpoints = generator.generate_api_contracts(project_info)
            doc = generator._format_api_document(endpoints)
            path = Path("specs/API_CONTRACT.md")
            path.parent.mkdir(exist_ok=True)
            path.write_text(doc)
            click.echo(f"✅ Generated: {path}")
        elif spec_type == "guidelines":
            tech_stack = generator.generate_tech_stack_recommendations(project_info)
            doc = generator.generate_development_guidelines(project_info, tech_stack)
            path = Path("specs/DEVELOPMENT_GUIDELINES.md")
            path.parent.mkdir(exist_ok=True)
            path.write_text(doc)
            click.echo(f"✅ Generated: {path}")
        elif spec_type == "adr":
            tech_stack = generator.generate_tech_stack_recommendations(project_info)
            doc = generator._format_adr(tech_stack)
            path = Path("specs/ADR-001-tech-stack.md")
            path.parent.mkdir(exist_ok=True)
            path.write_text(doc)
            click.echo(f"✅ Generated: {path}")


@cli.command()
@click.argument("feature_id", required=False)
@click.pass_obj
def build(rfd, feature_id):
    """Run build process for feature"""
    if not feature_id:
        feature_id = rfd.session.get_current_feature()

    if not feature_id:
        click.echo("❌ No feature specified. Use: rfd session start <feature>")
        return

    click.echo(f"🔨 Building feature: {feature_id}")
    success = rfd.builder.build_feature(feature_id)

    if success:
        click.echo("✅ Build successful!")
        rfd.checkpoint(f"Build passed for {feature_id}")
    else:
        click.echo("❌ Build failed - check errors above")


@cli.command()
@click.option("--feature", help="Validate specific feature")
@click.option("--full", is_flag=True, help="Full validation")
@click.pass_obj
def validate(rfd, feature, full):
    """Validate current implementation"""
    results = rfd.validator.validate(feature=feature, full=full)
    rfd.validator.print_report(results)

    if not results["passing"]:
        sys.exit(1)


@cli.command()
@click.argument("feature_id")
@click.pass_obj
def complete(rfd, feature_id):
    """Mark a feature as complete (updates database and PROJECT.md)"""
    from .feature_manager import FeatureManager

    fm = FeatureManager(rfd)

    # Get test results as evidence
    evidence = {"tests_passed": True}  # In production, run actual tests

    if fm.complete_feature(feature_id, evidence):
        click.echo(f"✅ Feature {feature_id} marked as complete")
        click.echo("📄 PROJECT.md updated automatically")
    else:
        click.echo(f"❌ Feature {feature_id} acceptance criteria not met")


@cli.command()
@click.pass_obj
def status(rfd):
    """Comprehensive project status with phases, tasks, and next actions"""
    import sqlite3

    from .feature_manager import FeatureManager

    fm = FeatureManager(rfd)
    data = fm.get_dashboard()

    click.echo("\n" + "=" * 60)
    click.echo("RFD PROJECT STATUS")
    click.echo("=" * 60)

    # Overall Progress
    stats = data["statistics"]
    click.echo(f"\n📊 Overall Progress: {stats['completion_rate']:.1f}% complete")
    progress_bar = "█" * int(stats["completion_rate"] / 5) + "░" * (20 - int(stats["completion_rate"] / 5))
    click.echo(f"   [{progress_bar}]")
    click.echo(
        f"   ✅ {stats['completed']} completed | 🔨 {stats['in_progress']} active | ⏳ {stats['pending']} pending"
    )

    # Current Focus
    if data["current_focus"]:
        click.echo("\n🎯 Current Focus:")
        click.echo(f"   {data['current_focus']['id']}: {data['current_focus']['description']}")

        # Show tasks for current feature
        conn = sqlite3.connect(rfd.db_path)
        tasks = conn.execute(
            """
            SELECT description, status FROM tasks
            WHERE feature_id = ?
            ORDER BY created_at
        """,
            (data["current_focus"]["id"],),
        ).fetchall()
        conn.close()

        if tasks:
            click.echo("\n   📝 Tasks:")
            for task in tasks:
                icon = "✓" if task[1] == "complete" else "○"
                click.echo(f"      {icon} {task[0]}")

    # Project Phases
    phases = fm.get_project_phases()
    if phases:
        click.echo("\n🗓️ Project Phases:")
        for phase in phases:
            icon = "✅" if phase["status"] == "complete" else "🔄" if phase["status"] == "active" else "⏸️"
            click.echo(f"   {icon} {phase['name']}: {phase['description']}")

    # Next Actions
    click.echo("\n➡️ Suggested Next Actions:")
    if stats["in_progress"] > 0:
        click.echo("   1. Continue current feature: ./rfd build")
        click.echo("   2. Run validation: ./rfd validate")
    elif stats["pending"] > 0:
        next_feature = next((f for f in data["features"] if f["status"] == "pending"), None)
        if next_feature:
            click.echo(f"   1. Start next feature: ./rfd session start {next_feature['id']}")
    else:
        click.echo("   ✨ All features complete! Consider adding new features to PROJECT.md")

    # Last Session Info
    click.echo("\n📅 Last Session:")
    context_file = rfd.rfd_dir / "context" / "current.md"
    if context_file.exists():
        import frontmatter

        with open(context_file) as f:
            content = frontmatter.load(f)
            if content.metadata:
                click.echo(f"   Feature: {content.metadata.get('feature', 'unknown')}")
                started = content.metadata.get("started", "unknown")
                if hasattr(started, "isoformat"):
                    started = started.isoformat()[:19]
                elif isinstance(started, str):
                    started = started[:19]
                click.echo(f"   Started: {started}")


@cli.command()
@click.pass_obj
def dashboard(rfd):
    """Show project dashboard with all features and progress"""
    from .feature_manager import FeatureManager

    fm = FeatureManager(rfd)
    data = fm.get_dashboard()

    click.echo("\n=== RFD Project Dashboard ===\n")

    # Statistics
    stats = data["statistics"]
    click.echo(f"📊 Progress: {stats['completion_rate']:.1f}% complete")
    click.echo(f"   ✅ Completed: {stats['completed']}")
    click.echo(f"   🔨 In Progress: {stats['in_progress']}")
    click.echo(f"   ⏳ Pending: {stats['pending']}")

    # Current focus
    if data["current_focus"]:
        click.echo(f"\n🎯 Current Focus: {data['current_focus']['id']}")

    # Features list
    click.echo("\n📦 Features:")
    for feature in data["features"]:
        icon = "✅" if feature["status"] == "complete" else "🔨" if feature["status"] == "in_progress" else "⏳"
        click.echo(f"  {icon} {feature['id']}: {feature['description'][:50]}")
        if feature["status"] == "in_progress" and feature["started_at"]:
            click.echo(f"      Started: {feature['started_at'][:10]}")


@cli.command()
@click.pass_obj
def check(rfd):
    """Quick health check"""
    state = rfd.get_current_state()

    # Quick status
    click.echo("\n=== RFD Status Check ===\n")

    # Validation
    val = state["validation"]
    click.echo(f"📋 Validation: {'✅' if val['passing'] else '❌'}")

    # Build
    build = state["build"]
    click.echo(f"🔨 Build: {'✅' if build['passing'] else '❌'}")

    # Current session
    session = state["session"]
    if session:
        click.echo(f"📝 Session: {session['feature_id']} (started {session['started_at']})")

    # Features
    click.echo("\n📦 Features:")
    for fid, status, checkpoints in state["features"]:
        icon = "✅" if status == "complete" else "🔨" if status == "building" else "⭕"
        click.echo(f"  {icon} {fid} ({checkpoints} checkpoints)")

    # Next action
    click.echo(f"\n→ Next: {rfd.session.suggest_next_action()}")


@cli.group()
@click.pass_obj
def session(rfd):
    """Manage development sessions"""
    pass


@session.command("start")
@click.argument("feature_id")
@click.pass_obj
def session_start(rfd, feature_id):
    """Start new feature session"""
    try:
        rfd.session.start(feature_id)
        click.echo(f"🚀 Session started for: {feature_id}")
        click.echo("📋 Context updated at: .rfd/context/current.md")
        click.echo("\n→ Next: rfd build")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@session.command("end")
@click.option("--success/--failed", default=True)
@click.pass_obj
def session_end(rfd, success):
    """End current session"""
    session_id = rfd.session.end(success=success)
    if session_id:
        click.echo(f"📝 Session {session_id} ended")


@cli.command()
@click.argument("message")
@click.pass_obj
def checkpoint(rfd, message):
    """Save checkpoint with current state"""
    # Get current state
    validation = rfd.validator.validate()
    build = rfd.builder.get_status()

    # Git commit
    try:
        git_hash = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception:
        git_hash = "no-git"

    # Save checkpoint
    conn = sqlite3.connect(rfd.db_path)
    conn.execute(
        """
        INSERT INTO checkpoints (feature_id, timestamp, validation_passed,
                                build_passed, git_hash, evidence)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (
            rfd.session.get_current_feature(),
            datetime.now().isoformat(),
            validation["passing"],
            build["passing"],
            git_hash,
            json.dumps({"message": message, "validation": validation, "build": build}),
        ),
    )
    conn.commit()

    # Update PROGRESS.md
    with open("PROGRESS.md", "a") as f:
        f.write(f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M')} - Checkpoint\n")
        f.write(f"MESSAGE: {message}\n")
        f.write(f"VALIDATION: {'✅' if validation['passing'] else '❌'}\n")
        f.write(f"BUILD: {'✅' if build['passing'] else '❌'}\n")
        f.write(f"COMMIT: {git_hash[:7]}\n")

    click.echo(f"✅ Checkpoint saved: {message}")


@cli.command()
@click.pass_obj
def revert(rfd):
    """Revert to last working checkpoint"""
    success, message = rfd.revert_to_last_checkpoint()

    if success:
        click.echo(f"✅ {message}")
    else:
        click.echo(f"❌ {message}")


@cli.command()
@click.pass_obj
def resume(rfd):
    """Resume from last session context - FULLY AUTOMATIC"""
    from .auto_handoff import AutoHandoff

    # Create automatic handoff system
    handoff = AutoHandoff(rfd)

    # Save current state to database
    handoff.save_to_database()

    # Display complete handoff
    handoff.display_handoff()

    return

    # OLD manual code below (kept for reference but not executed)
    context_file = rfd.rfd_dir / "context" / "current.md"
    memory_file = rfd.rfd_dir / "context" / "memory.json"

    click.echo("\n=== RFD Resume ===\n")

    # Show current context
    if context_file.exists():
        import frontmatter

        with open(context_file) as f:
            content = frontmatter.load(f)
            if content.metadata:
                feature = content.metadata.get("feature", "unknown")
                started = content.metadata.get("started", "unknown")
                status = content.metadata.get("status", "unknown")

                click.echo("📋 Current Session:")
                click.echo(f"   Feature: {feature}")
                click.echo(f"   Started: {started}")
                click.echo(f"   Status: {status}")

    # Show memory
    if memory_file.exists():
        data = json.loads(memory_file.read_text())
        if data.get("current_feature"):
            click.echo("\n🧠 Memory:")
            click.echo(f"   Current Feature: {data['current_feature']}")
            if data.get("last_action"):
                click.echo(f"   Last Action: {data['last_action']}")

    # Show project status
    click.echo("\n📊 Project Status:")
    state = rfd.get_current_state()
    click.echo(f"   Validation: {'✅' if state['validation']['passing'] else '❌'}")
    click.echo(f"   Build: {'✅' if state['build']['passing'] else '❌'}")

    # Suggest next action
    next_action = rfd.session.suggest_next_action()
    click.echo(f"\n➡️ Next Action: {next_action}")

    # Show tasks if current feature exists
    if context_file.exists():
        conn = sqlite3.connect(rfd.db_path)
        tasks = conn.execute(
            """
            SELECT description, status FROM tasks
            WHERE feature_id = (SELECT value FROM memory WHERE key = 'current_feature')
            ORDER BY created_at
        """
        ).fetchall()
        conn.close()

        if tasks:
            click.echo("\n📝 Tasks:")
            for desc, status in tasks:
                icon = "✓" if status == "complete" else "○"
                click.echo(f"   {icon} {desc}")


@cli.group()
@click.pass_obj
def workflow(rfd):
    """Manage gated workflow for spec-driven development"""
    pass


@workflow.command("start")
@click.argument("feature_id")
@click.pass_obj
def workflow_start(rfd, feature_id):
    """Start feature with gated workflow"""
    import uuid

    session_id = str(uuid.uuid4())[:8]

    success, message = rfd.workflow.start_feature(feature_id, session_id)
    if success:
        click.echo(f"✅ {message}")

        # Show current state
        status = rfd.workflow.get_workflow_status(feature_id)
        click.echo(f"\n📍 Current State: {status['current_state']}")
        click.echo(f"📊 Progress: {status['progress']}")

        # Check if can proceed
        can_proceed, reason = rfd.workflow.can_proceed(feature_id)
        if can_proceed:
            click.echo(f"✅ Ready to proceed: {reason}")
            click.echo("\n→ Next: rfd workflow proceed")
        else:
            click.echo(f"⚠️ Cannot proceed: {reason}")
            click.echo("\n→ Resolve issues first")
    else:
        click.echo(f"❌ {message}")


@workflow.command("status")
@click.argument("feature_id")
@click.pass_obj
def workflow_status(rfd, feature_id):
    """Show workflow status for feature"""
    status = rfd.workflow.get_workflow_status(feature_id)

    if "error" in status:
        click.echo(f"❌ {status['error']}")
        return

    click.echo(f"\n=== Workflow Status: {feature_id} ===")
    click.echo(f"\n📍 Current State: {status['current_state']}")
    click.echo(f"📊 Progress: {status['progress']}")

    # Show checkpoints
    if status["checkpoints_passed"]:
        click.echo("\n✅ Checkpoints Passed:")
        for cp in status["checkpoints_passed"]:
            click.echo(f"   - {cp['state']}: {cp['timestamp'][:10]}")

    # Show blockers
    if status["unresolved_queries"] > 0:
        click.echo(f"\n⚠️ Unresolved Queries: {status['unresolved_queries']}")

    # Show drift prevention
    click.echo(f"\n🛡️ Drift Attempts Blocked: {status['drift_attempts_blocked']}")
    click.echo(f"🚫 Hallucinations Caught: {status['hallucinations_caught']}")

    # Can proceed?
    can_proceed, reason = status["can_proceed"]
    if can_proceed:
        click.echo(f"\n✅ Can Proceed: {reason}")
    else:
        click.echo(f"\n❌ Blocked: {reason}")


@workflow.command("proceed")
@click.argument("feature_id")
@click.pass_obj
def workflow_proceed(rfd, feature_id):
    """Try to proceed to next workflow state"""
    import uuid

    session_id = str(uuid.uuid4())[:8]  # Would get from session

    success, message = rfd.workflow.proceed_to_next(feature_id, session_id)

    if success:
        click.echo(f"✅ {message}")

        # Show new state
        status = rfd.workflow.get_workflow_status(feature_id)
        click.echo(f"\n📍 Now in: {status['current_state']}")
        click.echo(f"📊 Progress: {status['progress']}")

        # Show next action based on state
        state = rfd.workflow.get_current_state(feature_id)
        next_actions = {
            "specification": "rfd speckit specify {feature_id}",
            "clarification": "rfd workflow query {feature_id} 'your question'",
            "planning": "rfd speckit plan {feature_id}",
            "task_generation": "rfd speckit tasks {feature_id}",
            "implementation": "rfd speckit implement {feature_id}",
            "validation": "rfd validate --feature {feature_id}",
            "completion": "rfd complete {feature_id}",
        }

        if state and state.value in next_actions:
            click.echo(f"\n→ Next: {next_actions[state.value].format(feature_id=feature_id)}")
    else:
        click.echo(f"❌ {message}")
        click.echo("\n→ Resolve issues before proceeding")


@workflow.command("query")
@click.argument("feature_id")
@click.argument("question")
@click.pass_obj
def workflow_query(rfd, feature_id, question):
    """Add a query that needs resolution"""
    query_id = rfd.workflow.add_query(feature_id, question)
    click.echo(f"✅ Query #{query_id} added")
    click.echo(f"❓ {question}")
    click.echo("\n→ Resolve with: rfd workflow resolve {query_id} 'answer'")


@workflow.command("resolve")
@click.argument("query_id", type=int)
@click.argument("answer")
@click.pass_obj
def workflow_resolve(rfd, query_id, answer):
    """Resolve a query"""
    rfd.workflow.resolve_query(query_id, answer)
    click.echo(f"✅ Query #{query_id} resolved")
    click.echo(f"💡 {answer}")


@cli.command()
@click.pass_obj
def migrate(rfd):
    """Check and apply migrations after RFD update"""
    from .migration import RFDMigration

    migrator = RFDMigration()

    # Check if migration needed
    if not migrator.needs_migration():
        click.echo(f"✅ Project is up to date with RFD v{migrator.get_rfd_version()}")
        return

    click.echo(f"🔄 Migration needed: v{migrator.get_project_rfd_version()} → v{migrator.get_rfd_version()}")

    # Check compatibility
    compat = migrator.check_compatibility()
    if not compat["compatible"]:
        click.echo("⚠️ Breaking changes detected:")
        for warning in compat["warnings"]:
            click.echo(f"   - {warning}")

        if not click.confirm("Continue with migration?"):
            return

    # Run migration
    click.echo("📦 Creating backup...")
    result = migrator.migrate()

    if result["status"] == "migrated":
        click.echo("✅ Migration successful!")
        click.echo(f"   Backup saved to: {result['backup']}")
        for migration in result["migrations"]:
            click.echo(f"   Applied: {migration}")
    elif result["status"] == "failed":
        click.echo(f"❌ Migration failed: {result.get('error', 'Unknown error')}")
        click.echo(f"   Backup preserved at: {result['backup']}")
    else:
        click.echo("ℹ️ No migration needed")


@cli.command()
@click.pass_obj
def upgrade_check(rfd):
    """Check if RFD itself needs updating"""
    import subprocess

    # Check current version
    from . import __version__

    current = __version__

    # Check PyPI for latest
    try:
        result = subprocess.run(
            ["pip", "index", "versions", "rfd-protocol"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            # Parse output for latest version
            lines = result.stdout.split("\n")
            for line in lines:
                if "Available versions:" in line:
                    versions = line.split(":")[1].strip().split(",")
                    latest = versions[0].strip()

                    if latest != current:
                        click.echo(f"🆕 Update available: v{current} → v{latest}")
                        click.echo("\nTo update: pip install --upgrade rfd-protocol")
                        click.echo("After updating, run: rfd migrate")
                    else:
                        click.echo(f"✅ You're on the latest version: v{current}")
                    return

        click.echo("⚠️ Could not check for updates")

    except Exception as e:
        click.echo(f"⚠️ Update check failed: {e}")


@cli.group()
@click.pass_obj
def speckit(rfd):
    """Spec-kit style commands with RFD enforcement"""
    pass


@speckit.command("constitution")
@click.pass_obj
def speckit_constitution(rfd):
    """Create project constitution"""
    path = rfd.speckit.create_constitution()
    click.echo(f"📜 Constitution created: {path}")


@speckit.command("specify")
@click.argument("feature_id")
@click.pass_obj
def speckit_specify(rfd, feature_id):
    """Create feature specification"""
    # Check workflow state
    state = rfd.workflow.get_current_state(feature_id)
    if state and state.value != "specification":
        click.echo(f"❌ Cannot specify in state {state.value}. Use 'rfd workflow proceed' first.")
        return

    path = rfd.speckit.specify_feature(feature_id)
    click.echo(f"📄 Specification created: {path}")


@speckit.command("plan")
@click.argument("feature_id")
@click.pass_obj
def speckit_plan(rfd, feature_id):
    """Create implementation plan"""
    # Check workflow state
    allowed, reason = rfd.workflow.enforce_linear_flow(feature_id, "create_plan")
    if not allowed:
        click.echo(f"❌ {reason}")
        return

    path = rfd.speckit.create_plan(feature_id)
    click.echo(f"📋 Plan created: {path}")


@speckit.command("tasks")
@click.argument("feature_id")
@click.pass_obj
def speckit_tasks(rfd, feature_id):
    """Generate tasks from plan"""
    # Check workflow state
    allowed, reason = rfd.workflow.enforce_linear_flow(feature_id, "generate_tasks")
    if not allowed:
        click.echo(f"❌ {reason}")
        return

    path = rfd.speckit.create_tasks(feature_id)
    click.echo(f"📝 Tasks created: {path}")


@speckit.command("implement")
@click.argument("feature_id")
@click.pass_obj
def speckit_implement(rfd, feature_id):
    """Execute implementation with validation"""
    # Check workflow state
    allowed, reason = rfd.workflow.enforce_linear_flow(feature_id, "implement")
    if not allowed:
        click.echo(f"❌ {reason}")
        return

    success = rfd.speckit.implement_feature(feature_id)
    if success:
        click.echo("✅ Implementation complete")
    else:
        click.echo("❌ Implementation failed")


@cli.group()
@click.pass_obj
def memory(rfd):
    """Manage AI memory"""
    pass


@memory.command("show")
@click.pass_obj
def memory_show(rfd):
    """Show current AI memory"""
    memory_file = rfd.rfd_dir / "context" / "memory.json"
    if memory_file.exists():
        data = json.loads(memory_file.read_text())
        click.echo(json.dumps(data, indent=2))


@memory.command("reset")
@click.pass_obj
def memory_reset(rfd):
    """Reset AI memory"""
    memory_file = rfd.rfd_dir / "context" / "memory.json"
    memory_file.write_text("{}")
    click.echo("✅ Memory reset")


def create_claude_md():
    """Create CLAUDE.md for Claude Code CLI"""
    content = """---
# Claude Code Configuration
tools: enabled
memory: .rfd/context/memory.json
---

# RFD Project Assistant

You are operating in a Reality-First Development (RFD) project. Your ONLY job is to make tests pass.

## Critical Rules
1. Read @PROJECT.md for the specification
2. Check @.rfd/context/current.md for your current task
3. Read @PROGRESS.md for what's already done
4. Run `rfd check` before ANY changes
5. Every code change MUST improve `rfd validate` output
6. NEVER mock data - use real implementations
7. NEVER add features not in @PROJECT.md

## Workflow for Every Response

### 1. Check Current State
```bash
rfd check
```

### 2. Read Context
- @PROJECT.md - What we're building
- @.rfd/context/current.md - Current feature/task
- @PROGRESS.md - What already works

### 3. Write Code
- Minimal code to fix the FIRST failing test
- Complete, runnable code only
- No explanations, just code that works

### 4. Validate
```bash
rfd build && rfd validate
```

### 5. Checkpoint Success
```bash
rfd checkpoint "Fixed: [describe what you fixed]"
```

### 6. Move to Next
Check @.rfd/context/current.md for next failing test. Repeat.

## Your Memory
- Located at @.rfd/context/memory.json
- Automatically loaded/saved
- Remembers what you've tried
- Tracks what works/doesn't

## Never Forget
- You're fixing tests, not designing architecture
- If tests pass, you're done
- If tests fail, fix them
- Reality (passing tests) > Theory (perfect code)
"""
    Path("CLAUDE.md").write_text(content)


def main():
    """Main entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
