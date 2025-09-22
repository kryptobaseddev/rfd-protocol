#!/bin/bash
# RFD Protocol Quick Setup Script
# Usage: curl -sSL https://raw.githubusercontent.com/nexus-dev/rfd-protocol/main/scripts/quick-setup.sh | bash

set -e

echo "🚀 RFD Protocol Quick Setup"
echo "=============================="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION found"

# Install RFD Protocol
echo "📦 Installing RFD Protocol..."
pip3 install nexus-rfd-protocol

# Verify installation
if command -v rfd &> /dev/null; then
    RFD_VERSION=$(rfd --version 2>/dev/null || echo "unknown")
    echo "✅ RFD Protocol installed: $RFD_VERSION"
else
    echo "⚠️  RFD command not found in PATH"
    echo "   Try: export PATH=\"\$PATH:\$HOME/.local/bin\""
    echo "   Or use: python3 -m nexus_rfd_protocol.cli"
fi

# Check if we're in a directory that looks like a project
if [[ -f "package.json" || -f "requirements.txt" || -f "go.mod" || -f "Cargo.toml" ]]; then
    echo ""
    echo "📁 Existing project detected!"
    read -p "Initialize RFD in current directory? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rfd init
        echo "✅ RFD initialized in existing project"
    fi
else
    echo ""
    echo "🎯 Ready to create a new project!"
    echo "Options:"
    echo "  1. rfd init                    # Interactive setup"
    echo "  2. python3 setup-project.py   # Template-based setup"
    echo ""
    read -p "Create new project now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Project name: " PROJECT_NAME
        if [[ -n "$PROJECT_NAME" ]]; then
            mkdir -p "$PROJECT_NAME"
            cd "$PROJECT_NAME"
            rfd init
            echo "✅ New project '$PROJECT_NAME' created!"
        fi
    fi
fi

echo ""
echo "🎉 Setup complete! Next steps:"
echo "   rfd spec review      # Review your specification"
echo "   rfd session start    # Start building features"
echo "   rfd check           # Check project status"
echo ""
echo "📚 Documentation: https://github.com/nexus-dev/rfd-protocol"
echo "💬 Support: https://github.com/nexus-dev/rfd-protocol/issues"