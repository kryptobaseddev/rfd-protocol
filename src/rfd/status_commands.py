"""
Status and dashboard commands extracted from CLI to reduce line count
"""

import sqlite3

import click


def show_project_status(rfd):
    """Comprehensive project status with phases, tasks, and next actions"""
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

        if tasks:
            click.echo("\n📝 Current Tasks:")
            for desc, status in tasks:
                icon = "✅" if status == "complete" else "🔨" if status == "in_progress" else "⏳"
                click.echo(f"   {icon} {desc}")

    # Phase Status
    click.echo("\n🔄 Project Phases:")
    conn = sqlite3.connect(rfd.db_path)
    phases = conn.execute("SELECT name, status, order_index FROM project_phases ORDER BY order_index").fetchall()

    if phases:
        for name, status, _ in phases:
            icon = "✅" if status == "complete" else "🔨" if status == "active" else "⏳"
            click.echo(f"   {icon} {name}")
    else:
        click.echo("   No phases configured")

    # Recent Activity
    checkpoints = conn.execute(
        """
        SELECT c.timestamp, c.feature_id, c.validation_passed, c.build_passed
        FROM checkpoints c
        ORDER BY c.timestamp DESC LIMIT 3
    """
    ).fetchall()

    if checkpoints:
        click.echo("\n📈 Recent Activity:")
        for timestamp, feature_id, val, build in checkpoints:
            val_icon = "✅" if val else "❌"
            build_icon = "✅" if build else "❌"
            date = timestamp[:10] if timestamp else "unknown"
            click.echo(f"   {date} {feature_id}: {val_icon} validation {build_icon} build")

    # Next Actions
    click.echo("\n➡️  Next Actions:")
    if not data["current_focus"]:
        pending_features = [f for f in data["features"] if f["status"] == "pending"]
        if pending_features:
            first = pending_features[0]
            click.echo(f"   rfd session start {first['id']}")
        else:
            click.echo("   All features complete! 🎉")
    else:
        # Suggest based on validation state
        current_id = data["current_focus"]["id"]
        validation = rfd.validator.validate(feature=current_id)
        if not validation["passing"]:
            click.echo(f"   rfd validate --feature {current_id}")
        else:
            click.echo(f"   rfd checkpoint 'Progress on {current_id}'")

    conn.close()


def show_dashboard(rfd):
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


def show_quick_check(rfd):
    """Quick health check"""
    from pathlib import Path

    from .template_sync import auto_sync_on_init
    from .update_check import check_for_updates

    # Check for updates (once per day max)
    check_for_updates()

    # Auto-sync templates on check
    auto_sync_on_init(Path.cwd())

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

    # Next action suggestion
    click.echo(f"\n→ Next: {rfd.session.suggest_next_action()}")
