"""
Clean RFD CLI - Simplified command structure without speckit subcommand
"""

import click

from .rfd import RFD


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """RFD: Reality-First Development Protocol"""
    ctx.ensure_object(dict)
    ctx.obj = RFD()

    # If no command given, show status (intuitive!)
    if ctx.invoked_subcommand is None:
        ctx.invoke(check)


# ============= INITIALIZATION =============


@cli.command()
@click.option("--wizard", is_flag=True, help="Run interactive wizard")
@click.option("--from-prd", type=click.Path(exists=True), help="Initialize from PRD")
@click.option("--mode", type=click.Choice(["greenfield", "brownfield"]), default="greenfield", help="Project mode")
@click.pass_obj
def init(rfd, wizard, from_prd, mode):
    """Initialize RFD in current directory"""
    # Implementation here
    pass


# ============= SPECIFICATION =============


@cli.group(invoke_without_command=True)
@click.pass_context
def spec(ctx):
    """Manage project specifications"""
    if ctx.invoked_subcommand is None:
        # Default: show current spec
        ctx.invoke(spec_review)


@spec.command("review")
@click.pass_obj
def spec_review(rfd):
    """Review current specification"""
    # Show PROJECT.md content
    pass


@spec.command("init")
@click.option("--interactive", is_flag=True, help="Interactive mode")
@click.pass_obj
def spec_init(rfd, interactive):
    """Create initial specification (was: spec create)"""
    # Create PROJECT.md
    pass


@spec.command("constitution")
@click.pass_obj
def spec_constitution(rfd):
    """Generate immutable project principles"""
    path = rfd.speckit.create_constitution()
    click.echo(f"📜 Constitution created: {path}")


@spec.command("clarify")
@click.argument("feature_id", required=False)
@click.pass_obj
def spec_clarify(rfd, feature_id):
    """Identify and resolve specification ambiguities"""
    # Analyze spec for unclear areas
    pass


@spec.command("validate")
@click.pass_obj
def spec_validate(rfd):
    """Validate specification completeness"""
    # Check spec has all required fields
    pass


# ============= PLANNING =============


@cli.group(invoke_without_command=True)
@click.pass_context
def plan(ctx):
    """Project planning and task management"""
    if ctx.invoked_subcommand is None:
        # Default: show current plan or generate
        ctx.invoke(plan_show)


@plan.command("show")
@click.pass_obj
def plan_show(rfd):
    """Show current implementation plan"""
    # Display plan if exists
    pass


@plan.command("create")
@click.argument("feature_id")
@click.pass_obj
def plan_create(rfd, feature_id):
    """Create implementation plan for feature"""
    path = rfd.speckit.create_plan(feature_id)
    click.echo(f"📋 Plan created: {path}")


@plan.command("tasks")
@click.argument("feature_id")
@click.option("--parallel/--sequential", default=False, help="Mark tasks as parallelizable")
@click.pass_obj
def plan_tasks(rfd, feature_id, parallel):
    """Generate task breakdown from plan"""
    path = rfd.speckit.create_tasks(feature_id)
    click.echo(f"📝 Tasks created: {path}")


@plan.command("phases")
@click.pass_obj
def plan_phases(rfd):
    """Define or show project phases"""
    # Show/create project phases
    pass


# ============= ANALYSIS =============


@cli.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
@click.option("--scope", type=click.Choice(["all", "spec", "tasks", "api", "tests"]), default="all")
@click.pass_obj
def analyze(rfd, format, scope):
    """Cross-artifact consistency analysis"""
    from .analyze import ArtifactAnalyzer

    analyzer = ArtifactAnalyzer(rfd)
    analysis = analyzer.analyze_cross_artifact_consistency()

    if format == "json":
        import json

        click.echo(json.dumps(analysis, indent=2))
    else:
        report = analyzer.generate_report(analysis)
        click.echo(report)


# ============= CORE WORKFLOW =============


@cli.group()
@click.pass_obj
def session(rfd):
    """Manage development sessions"""
    pass


@session.command("start")
@click.argument("feature_id")
@click.pass_obj
def session_start(rfd, feature_id):
    """Start working on a feature"""
    rfd.session.start_session(feature_id)
    click.echo(f"✅ Started session for feature: {feature_id}")


@session.command("end")
@click.pass_obj
def session_end(rfd):
    """End current session"""
    rfd.session.end_session()
    click.echo("✅ Session ended")


@cli.command()
@click.argument("feature", required=False)
@click.pass_obj
def build(rfd, feature):
    """Build current or specified feature"""
    result = rfd.builder.build(feature)
    if result["success"]:
        click.echo("✅ Build successful")
    else:
        click.echo(f"❌ Build failed: {result.get('error')}")


@cli.command()
@click.option("--feature", help="Specific feature to validate")
@click.option("--verbose", is_flag=True, help="Verbose output")
@click.pass_obj
def validate(rfd, feature, verbose):
    """Validate implementation against specification"""
    results = rfd.validator.validate(feature_id=feature)

    # Display results
    for result in results:
        if result["passed"]:
            click.echo(f"✅ {result['test']}: {result.get('message', 'Passed')}")
        else:
            click.echo(f"❌ {result['test']}: {result.get('message', 'Failed')}")


@cli.command()
@click.argument("message")
@click.pass_obj
def checkpoint(rfd, message):
    """Save current progress"""
    success = rfd.session.checkpoint(message)
    if success:
        click.echo(f"✅ Checkpoint saved: {message}")
    else:
        click.echo("❌ Cannot checkpoint - validation failing")


# ============= STATUS & REVIEW =============


@cli.command()
@click.pass_obj
def check(rfd):
    """Quick status check"""
    # Show current state
    validation_status = "✅" if rfd.validator.is_valid() else "❌"
    build_status = "✅" if rfd.builder.last_build_success() else "❌"

    click.echo("\n=== RFD Status Check ===\n")
    click.echo(f"📋 Validation: {validation_status}")
    click.echo(f"🔨 Build: {build_status}")

    # Current session
    session = rfd.session.get_active_session()
    if session:
        click.echo(f"📝 Session: {session['feature_id']} (started {session['started_at']})")
    else:
        click.echo("📝 Session: None active")

    # Features
    features = rfd.spec.get_features()
    click.echo("\n📦 Features:")
    for feature in features:
        status_icon = "✅" if feature["status"] == "complete" else "⏳"
        click.echo(f"  {status_icon} {feature['id']} ({feature.get('checkpoints', 0)} checkpoints)")

    # Suggest next action
    click.echo(f"\n→ Next: {rfd.session.suggest_next_action()}")


@cli.command()
@click.pass_obj
def status(rfd):
    """Detailed project status with visual progress"""
    # Implementation from existing status command
    pass


@cli.command()
@click.pass_obj
def dashboard(rfd):
    """Visual progress dashboard"""
    # Implementation from existing dashboard
    pass


# ============= STATE MANAGEMENT =============


@cli.command()
@click.option("--to", help="Checkpoint ID or timestamp to revert to")
@click.option("--list", "list_checkpoints", is_flag=True, help="List available checkpoints")
@click.pass_obj
def revert(rfd, to, list_checkpoints):
    """Revert to previous checkpoint"""
    if list_checkpoints:
        # Show available checkpoints
        pass
    else:
        # Revert to checkpoint
        pass


@cli.group()
@click.pass_obj
def memory(rfd):
    """Manage context memory"""
    pass


@memory.command("show")
@click.pass_obj
def memory_show(rfd):
    """Display current context memory"""
    # Show .rfd/context/memory.json
    pass


@memory.command("reset")
@click.option("--confirm", is_flag=True, help="Confirm reset")
@click.pass_obj
def memory_reset(rfd, confirm):
    """Clear context memory (use with caution!)"""
    if not confirm:
        click.echo("⚠️ This will clear all context memory. Use --confirm to proceed.")
        return
    # Reset memory
    pass


@cli.command()
@click.pass_obj
def migrate(rfd):
    """Migrate database after RFD update"""
    # Run migration
    pass


if __name__ == "__main__":
    cli()
