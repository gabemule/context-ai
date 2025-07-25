#!/bin/bash

# 🚀 Smart Development Installation Script
# Automatically detects and uninstalls local editable packages, then installs current project

set -e  # Exit on any error

echo "🔧 Starting smart development installation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a Python project directory
if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ]; then
    print_error "This script must be run from a Python project root directory (needs pyproject.toml or setup.py)"
    exit 1
fi

print_status "Checking Python environment..."
PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
print_status "Using Python $PYTHON_VERSION"

# Get current project name
CURRENT_PROJECT=""
if [ -f "pyproject.toml" ]; then
    CURRENT_PROJECT=$(python -c "
import toml
try:
    data = toml.load('pyproject.toml')
    print(data.get('project', {}).get('name', ''))
except:
    print('')
" 2>/dev/null || echo "")
fi

if [ -z "$CURRENT_PROJECT" ]; then
    print_warning "Could not detect current project name from pyproject.toml"
    CURRENT_PROJECT="unknown"
else
    print_status "Current project: $CURRENT_PROJECT"
fi

print_status "Detecting locally installed editable packages..."

# Find all editable packages (installed with pip install -e)
EDITABLE_PACKAGES=$(pip list -e --format=json 2>/dev/null | python -c "
import sys
import json
try:
    packages = json.load(sys.stdin)
    for pkg in packages:
        name = pkg.get('name', '').lower()
        # Skip if it's the current project
        if name != '$CURRENT_PROJECT'.lower():
            print(name)
except:
    pass
" 2>/dev/null || echo "")

if [ -z "$EDITABLE_PACKAGES" ]; then
    print_status "No conflicting editable packages found"
else
    print_warning "Found editable packages to remove:"
    echo "$EDITABLE_PACKAGES" | while read -r package; do
        if [ -n "$package" ]; then
            echo "  - $package"
        fi
    done
    
    print_status "Uninstalling conflicting editable packages..."
    echo "$EDITABLE_PACKAGES" | while read -r package; do
        if [ -n "$package" ]; then
            print_status "Uninstalling $package..."
            pip uninstall "$package" -y || print_warning "Failed to uninstall $package"
        fi
    done
fi

# Also check for the current project itself (in case it's already installed)
if pip show "$CURRENT_PROJECT" >/dev/null 2>&1; then
    print_status "Uninstalling existing installation of $CURRENT_PROJECT..."
    pip uninstall "$CURRENT_PROJECT" -y || print_warning "Failed to uninstall existing $CURRENT_PROJECT"
fi

print_status "Installing current project in development mode..."

# Install current project
if pip install -e .; then
    print_success "Project installed successfully!"
else
    print_error "Failed to install current project"
    exit 1
fi

print_status "Verifying installation..."

# Get the CLI command name (usually the project name with hyphens)
CLI_COMMAND=$(echo "$CURRENT_PROJECT" | tr '_' '-')

# Test the installation if we know the command name
if [ "$CURRENT_PROJECT" != "unknown" ] && command -v "$CLI_COMMAND" >/dev/null 2>&1; then
    print_success "✅ $CLI_COMMAND command is available!"
    
    # Test basic functionality
    print_status "Testing basic functionality..."
    if "$CLI_COMMAND" --version >/dev/null 2>&1; then
        print_success "✅ $CLI_COMMAND --version works!"
    else
        print_warning "⚠️  $CLI_COMMAND --version failed (might have dependency warnings)"
    fi
    
    if "$CLI_COMMAND" --help >/dev/null 2>&1; then
        print_success "✅ $CLI_COMMAND --help works!"
    else
        print_warning "⚠️  $CLI_COMMAND --help failed"
    fi
else
    print_warning "Could not verify CLI command (project name: $CURRENT_PROJECT)"
    print_status "You can manually test with: pip show $CURRENT_PROJECT"
fi

echo ""
print_success "🎉 Smart development installation completed successfully!"
echo ""
echo "📋 Summary:"
echo "  📦 Project: $CURRENT_PROJECT"
echo "  🐍 Python: $PYTHON_VERSION"
echo "  🔗 Mode: Editable install (pip install -e .)"
echo ""
echo "🔧 To uninstall: pip uninstall $CURRENT_PROJECT"
echo "🔄 To reinstall: ./dev-install.sh"
echo "📝 To see all packages: pip list"
