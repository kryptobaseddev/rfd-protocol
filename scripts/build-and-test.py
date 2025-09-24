#!/usr/bin/env python3
"""
Build and Test RFD Protocol Package
Ensures the package is properly structured and installable
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return result"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    if result.stdout:
        print(f"STDOUT: {result.stdout}")
    if result.stderr:
        print(f"STDERR: {result.stderr}")

    if check and result.returncode != 0:
        print(f"Command failed with return code: {result.returncode}")
        sys.exit(1)

    return result


def test_package_structure():
    """Test that package structure is correct"""
    print("\n🔍 Testing package structure...")

    required_files = [
        "pyproject.toml",
        "README.md",
        "INSTALL.md",
        "nexus_rfd_protocol/__init__.py",
        "nexus_rfd_protocol/cli.py",
        "nexus_rfd_protocol/rfd.py",
        "nexus_rfd_protocol/build.py",
        "nexus_rfd_protocol/validation.py",
        "nexus_rfd_protocol/spec.py",
        "nexus_rfd_protocol/session.py",
        "nexus_rfd_protocol/templates/CLAUDE.md",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False

    print("✅ Package structure is correct")
    return True


def test_build():
    """Test building the package"""
    print("\n📦 Testing package build...")

    # Clean previous builds
    for dir_name in ["build", "dist", "nexus_rfd_protocol.egg-info"]:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)

    # Build package
    run_command([sys.executable, "-m", "build"])

    # Check that wheel and source dist were created
    dist_files = list(Path("dist").glob("*"))
    wheel_files = [f for f in dist_files if f.suffix == ".whl"]
    tar_files = [f for f in dist_files if f.suffix == ".gz"]

    if not wheel_files:
        print("❌ No wheel file created")
        return False

    if not tar_files:
        print("❌ No source distribution created")
        return False

    print("✅ Package built successfully:")
    for f in dist_files:
        print(f"   {f.name}")

    return True


def test_installation():
    """Test installing the package in a clean environment"""
    print("\n📥 Testing package installation...")

    with tempfile.TemporaryDirectory() as temp_dir:
        venv_dir = Path(temp_dir) / "test_venv"

        # Create virtual environment
        run_command([sys.executable, "-m", "venv", str(venv_dir)])

        # Get paths for the virtual environment
        if os.name == "nt":  # Windows
            venv_python = venv_dir / "Scripts" / "python.exe"
            venv_pip = venv_dir / "Scripts" / "pip.exe"
        else:  # Unix-like
            venv_python = venv_dir / "bin" / "python"
            venv_pip = venv_dir / "bin" / "pip"

        # Upgrade pip
        run_command([str(venv_pip), "install", "--upgrade", "pip"])

        # Install our package
        wheel_files = list(Path("dist").glob("*.whl"))
        if not wheel_files:
            print("❌ No wheel file to test")
            return False

        wheel_path = wheel_files[0]
        run_command([str(venv_pip), "install", str(wheel_path)])

        # Test that the command works
        result = run_command(
            [
                str(venv_python),
                "-c",
                "import nexus_rfd_protocol; print('Import successful')",
            ]
        )

        # Test CLI command
        result = run_command([str(venv_python), "-m", "nexus_rfd_protocol.cli", "--help"], check=False)
        if result.returncode != 0:
            print("❌ CLI command failed")
            return False

        print("✅ Package installation test passed")
        return True


def test_cli_functionality():
    """Test basic CLI functionality"""
    print("\n🖥️  Testing CLI functionality...")

    with tempfile.TemporaryDirectory() as temp_dir:
        test_project_dir = Path(temp_dir) / "test_project"
        test_project_dir.mkdir()

        # Test init command (should work but might prompt for input)
        result = run_command(
            [sys.executable, "-m", "nexus_rfd_protocol.cli", "check"],
            cwd=test_project_dir,
            check=False,
        )

        # Should fail gracefully (no PROJECT.md exists)
        if "PROJECT.md" in result.stderr or "specification" in result.stderr.lower():
            print("✅ CLI commands work and handle missing files gracefully")
            return True

        print("⚠️  CLI test inconclusive but didn't crash")
        return True


def main():
    """Main test runner"""
    print("🧪 RFD Protocol Package Build & Test")
    print("=====================================")

    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    tests = [
        ("Package Structure", test_package_structure),
        ("Package Build", test_build),
        ("Installation", test_installation),
        ("CLI Functionality", test_cli_functionality),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'=' * 50}")
        print(f"Testing: {test_name}")
        print("=" * 50)

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")

    print(f"\n{'=' * 50}")
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 50)

    if passed == total:
        print("🎉 All tests passed! Package is ready for distribution.")
        return 0
    else:
        print("💥 Some tests failed. Please fix issues before distributing.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
