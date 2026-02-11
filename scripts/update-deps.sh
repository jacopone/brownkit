#!/usr/bin/env bash
# Update dependency lockfiles using pip-tools
#
# Usage: ./scripts/update-deps.sh

set -e

echo "📦 Updating dependency lockfiles..."

# Check if pip-tools is installed
if ! command -v pip-compile &> /dev/null; then
    echo "❌ pip-tools not installed. Installing..."
    pip install pip-tools
fi

# Compile production dependencies
echo "🔒 Compiling requirements.lock..."
pip-compile \
    --output-file=requirements.lock \
    --resolver=backtracking \
    pyproject.toml

# Compile development dependencies
echo "🔒 Compiling requirements-dev.lock..."
pip-compile \
    --output-file=requirements-dev.lock \
    --extra=dev \
    --resolver=backtracking \
    pyproject.toml

echo "✅ Dependency lockfiles updated!"
echo ""
echo "📝 To install dependencies:"
echo "   Production: pip install -r requirements.lock"
echo "   Development: pip install -r requirements-dev.lock"
