#!/usr/bin/env python3
"""
RFD Setup - Bulletproof initialization
Handles all environment setup automatically
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, check=True):
    """Run command with proper error handling"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if check and result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception running {cmd}: {e}")
        return False


def setup_environment():
    """Setup Python environment"""
    print("🔧 Setting up RFD environment...")

    # Check for Python
    if not run_command("python3 --version", check=False):
        print("❌ Python 3 is required")
        return False

    # Create virtual environment if needed
    if not Path(".venv").exists():
        print("→ Creating virtual environment...")
        if not run_command("python3 -m venv .venv"):
            # Try with uv
            if run_command("which uv", check=False):
                run_command("uv venv")
            else:
                print("❌ Failed to create virtual environment")
                return False

    # Install pip tools
    print("→ Installing package managers...")
    run_command("pip install --upgrade pip setuptools wheel", check=False)

    # Install uv if not present
    if not run_command("which uv", check=False):
        run_command("pip install uv", check=False)

    return True


def install_dependencies():
    """Install all required dependencies"""
    print("📦 Installing dependencies...")

    # Core dependencies
    deps = [
        "click>=8.0.0",
        "requests>=2.28.0",
        "pyyaml>=6.0",
        "questionary>=1.10.0",
        "python-frontmatter>=1.0.0",
        "tomli>=1.2.0",
        "ruff",
        "mypy",
        "pytest>=7.4.0",
        "pytest-cov>=4.1.0",
    ]

    for dep in deps:
        print(f"  → {dep}")
        run_command(f"pip install '{dep}'", check=False)

    return True


def setup_rfd_structure():
    """Create RFD directory structure"""
    print("📁 Setting up RFD structure...")

    dirs = [
        ".rfd",
        ".rfd/context",
        ".rfd/context/checkpoints",
        ".claude",
        ".claude/commands",
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")

    # Create default files
    files = {
        ".rfd/context/memory.json": "{}",
        ".rfd/rfd.db": "",
    }

    for file_path, content in files.items():
        path = Path(file_path)
        if not path.exists():
            path.write_text(content)
            print(f"  ✓ {file_path}")

    return True


def fix_permissions():
    """Fix file permissions"""
    print("🔐 Fixing permissions...")

    # Make scripts executable
    scripts = ["rfd", "setup.py"]
    for script in scripts:
        if Path(script).exists():
            run_command(f"chmod +x {script}")
            print(f"  ✓ {script}")

    return True


def verify_installation():
    """Verify everything is working"""
    print("\n✅ Verifying installation...")

    checks = {
        "Python": "python3 --version",
        "Click": "python3 -c 'import click'",
        "Frontmatter": "python3 -c 'import frontmatter'",
        "RFD structure": "ls -la .rfd/",
        "Claude commands": "ls -la .claude/commands/",
    }

    all_good = True
    for name, cmd in checks.items():
        if run_command(cmd, check=False):
            print(f"  ✓ {name}")
        else:
            print(f"  ✗ {name}")
            all_good = False

    return all_good


def main():
    """Main setup process"""
    print("=" * 50)
    print("RFD Protocol - Bulletproof Setup")
    print("=" * 50)

    steps = [
        ("Environment", setup_environment),
        ("Dependencies", install_dependencies),
        ("Structure", setup_rfd_structure),
        ("Permissions", fix_permissions),
        ("Verification", verify_installation),
    ]

    for name, func in steps:
        print(f"\n[{name}]")
        if not func():
            print(f"\n❌ Setup failed at: {name}")
            print("Run 'python3 setup.py' to retry")
            return 1

    print("\n" + "=" * 50)
    print("✅ RFD Setup Complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. Run: ./rfd init")
    print("  2. Run: ./rfd check")
    print("  3. Start building!")
    print("\nOr use Claude commands:")
    print("  /rfd-init")
    print("  /rfd-check")
    print("  /rfd-build")

    return 0


if __name__ == "__main__":
    sys.exit(main())
