#!/usr/bin/env python3
"""Check if .claude/commands/ is in sync with src/rfd/templates/commands/"""

import hashlib
from pathlib import Path
import sys


def get_file_hash(filepath: Path) -> str:
    """Get MD5 hash of a file for comparison."""
    if not filepath.exists():
        return ""
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def check_sync_status():
    """Check sync status between source templates and local .claude/commands/"""

    source_dir = Path("src/rfd/templates/commands")
    local_dir = Path(".claude/commands")

    if not source_dir.exists():
        print("❌ Source template directory not found: src/rfd/templates/commands/")
        return False

    if not local_dir.exists():
        print("❌ Local .claude/commands/ directory not found")
        return False

    all_synced = True
    issues = []

    # Check source -> local
    print("\n📋 Checking template sync status...\n")

    source_files = list(source_dir.glob("*.md"))
    local_files = list(local_dir.glob("*.md"))

    source_names = {f.name for f in source_files}
    local_names = {f.name for f in local_files}

    # Files in source but not in local
    missing_in_local = source_names - local_names
    if missing_in_local:
        all_synced = False
        issues.append(f"❌ Missing in .claude/commands/: {', '.join(sorted(missing_in_local))}")

    # Files in local but not in source
    extra_in_local = local_names - source_names
    if extra_in_local:
        all_synced = False
        issues.append(f"⚠️  Extra in .claude/commands/ (not in source): {', '.join(sorted(extra_in_local))}")

    # Check if files match
    for source_file in source_files:
        local_file = local_dir / source_file.name
        if local_file.exists():
            source_hash = get_file_hash(source_file)
            local_hash = get_file_hash(local_file)
            if source_hash != local_hash:
                all_synced = False
                issues.append(f"❌ Out of sync: {source_file.name}")

    # Report results
    if all_synced and not issues:
        print("✅ All templates are in sync!")
        print(f"   {len(source_files)} files in src/rfd/templates/commands/")
        print(f"   {len(local_files)} files in .claude/commands/")
    else:
        print("❌ Templates are NOT in sync!\n")
        for issue in issues:
            print(f"   {issue}")

        print("\n🔧 To fix:")
        print("   1. Copy from local to source: cp .claude/commands/*.md src/rfd/templates/commands/")
        print(
            '   2. Or sync from source to local: python -c "from src.rfd.template_sync import sync_templates; sync_templates()"'
        )
        print("   3. Or run: rfd audit  # To see violations in context")

    return all_synced


if __name__ == "__main__":
    synced = check_sync_status()
    sys.exit(0 if synced else 1)
