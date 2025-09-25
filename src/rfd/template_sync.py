"""
Template sync mechanism for RFD command templates.
Syncs command templates from installed RFD package to local project.
"""

import hashlib
import shutil
from pathlib import Path
from typing import Dict, List, Tuple


def get_file_hash(filepath: Path) -> str:
    """Get MD5 hash of a file for comparison."""
    if not filepath.exists():
        return ""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def get_template_source_dir() -> Path:
    """Get the source directory for RFD templates from installed package only."""
    # Only use installed package - true dogfooding, no local shortcuts
    try:
        import rfd

        package_dir = Path(rfd.__file__).parent
        templates_dir = package_dir / "templates" / "commands"
        if templates_dir.exists():
            return templates_dir

        # If templates don't exist in installed package, that's a package problem
        raise FileNotFoundError(
            f"Templates not found in installed RFD package at {templates_dir}. "
            "Please reinstall RFD or update to latest version."
        )
    except ImportError as e:
        raise ImportError("RFD package not installed. Install with: pip install rfd-protocol") from e


def sync_templates(project_dir: Path = None, force: bool = False) -> Tuple[List[str], List[str]]:
    """
    Sync command templates from RFD package to local project.

    Args:
        project_dir: Project directory (defaults to current working directory)
        force: Force overwrite even if files are modified locally

    Returns:
        Tuple of (updated_files, skipped_files)
    """
    if project_dir is None:
        project_dir = Path.cwd()

    # Ensure .claude/commands directory exists
    target_dir = project_dir / ".claude" / "commands"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Get source templates
    source_dir = get_template_source_dir()

    updated = []
    skipped = []

    # Sync each template file
    for source_file in source_dir.glob("*.md"):
        target_file = target_dir / source_file.name

        # Check if file needs update
        source_hash = get_file_hash(source_file)
        target_hash = get_file_hash(target_file)

        if source_hash != target_hash:
            if target_file.exists() and not force:
                # Check if local file has been modified
                # For now, we'll update unless force=False and file exists
                try:
                    shutil.copy2(source_file, target_file)
                    updated.append(source_file.name)
                except Exception as e:
                    skipped.append(f"{source_file.name}: {e}")
            else:
                shutil.copy2(source_file, target_file)
                updated.append(source_file.name)

    # Also sync CLAUDE.md if it exists
    claude_source = source_dir.parent / "CLAUDE.md"
    if claude_source.exists():
        claude_target = project_dir / ".claude" / "CLAUDE.md"
        if get_file_hash(claude_source) != get_file_hash(claude_target):
            shutil.copy2(claude_source, claude_target)
            updated.append("CLAUDE.md")

    return updated, skipped


def check_template_updates() -> Dict[str, bool]:
    """
    Check which templates need updating.

    Returns:
        Dict mapping filename to whether it needs update
    """
    project_dir = Path.cwd()
    target_dir = project_dir / ".claude" / "commands"

    if not target_dir.exists():
        # All templates need to be created
        source_dir = get_template_source_dir()
        return {f.name: True for f in source_dir.glob("*.md")}

    source_dir = get_template_source_dir()
    needs_update = {}

    for source_file in source_dir.glob("*.md"):
        target_file = target_dir / source_file.name
        source_hash = get_file_hash(source_file)
        target_hash = get_file_hash(target_file)
        needs_update[source_file.name] = source_hash != target_hash

    return needs_update


def auto_sync_on_init(project_dir: Path = None) -> None:
    """
    Automatically sync templates when RFD is initialized in a project.
    This should be called during 'rfd init' or when RFD detects version change.
    """
    if project_dir is None:
        project_dir = Path.cwd()

    # Check if this is an RFD project
    rfd_dir = project_dir / ".rfd"
    if not rfd_dir.exists():
        return

    # Check for version file to detect updates
    version_file = rfd_dir / ".template_version"

    try:
        import rfd

        current_version = getattr(rfd, "__version__", "unknown")
    except ImportError:
        # No RFD package installed - skip sync
        return

    # Check if version has changed
    needs_sync = True
    if version_file.exists():
        stored_version = version_file.read_text().strip()
        needs_sync = stored_version != current_version

    if needs_sync:
        try:
            updated, skipped = sync_templates(project_dir)

            # Update version file
            version_file.write_text(current_version)

            if updated:
                print(f"✅ Updated {len(updated)} command template(s) from RFD v{current_version}")
            if skipped:
                print(f"⚠️  Skipped {len(skipped)} file(s)")
        except FileNotFoundError as e:
            # Templates not in installed package - notify user
            print(f"⚠️  {e}")
        except Exception as e:
            print(f"⚠️  Could not sync templates: {e}")
