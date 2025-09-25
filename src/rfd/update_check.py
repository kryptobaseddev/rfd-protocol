"""
Check for RFD package updates from PyPI.
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

try:
    from packaging import version

    HAS_PACKAGING = True
except ImportError:
    HAS_PACKAGING = False


def check_pypi_version(package_name: str = "rfd-protocol") -> str | None:
    """
    Check the latest version of RFD on PyPI.

    Returns:
        Latest version string or None if check fails
    """
    try:
        result = subprocess.run(["pip", "index", "versions", package_name], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            # Parse output to find available versions
            lines = result.stdout.split("\n")
            for line in lines:
                if "Available versions:" in line:
                    # Extract first version (latest)
                    versions = line.split(":", 1)[1].strip()
                    latest = versions.split(",")[0].strip()
                    return latest
        return None
    except Exception:
        return None


def get_installed_version() -> str:
    """Get the currently installed RFD version."""
    try:
        import rfd

        return getattr(rfd, "__version__", "0.0.0")
    except ImportError:
        return "0.0.0"


def check_for_updates(silent: bool = False) -> bool:
    """
    Check if a newer version is available.

    Args:
        silent: If True, don't print messages

    Returns:
        True if update is available
    """
    # Skip if packaging module not available
    if not HAS_PACKAGING:
        return False

    # Check at most once per day to avoid spamming PyPI
    cache_file = Path.home() / ".rfd" / ".update_check"
    cache_file.parent.mkdir(exist_ok=True)

    if cache_file.exists():
        # Check if cache is fresh (less than 1 day old)
        cache_data = json.loads(cache_file.read_text())
        last_check = datetime.fromisoformat(cache_data.get("last_check", "2000-01-01"))
        if datetime.now() - last_check < timedelta(days=1):
            # Use cached result
            latest = cache_data.get("latest_version")
            if latest:
                current = get_installed_version()
                if version.parse(latest) > version.parse(current):
                    if not silent:
                        print(f"🆕 RFD update available: {current} → {latest}")
                        print("   Run: pip install --upgrade rfd-protocol")
                    return True
            return False

    # Check PyPI for latest version
    latest = check_pypi_version()
    if latest:
        # Cache the result
        cache_data = {"last_check": datetime.now().isoformat(), "latest_version": latest}
        cache_file.write_text(json.dumps(cache_data))

        # Compare versions
        current = get_installed_version()
        if version.parse(latest) > version.parse(current):
            if not silent:
                print(f"🆕 RFD update available: {current} → {latest}")
                print("   Run: pip install --upgrade rfd-protocol")
            return True

    return False
