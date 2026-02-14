#!/bin/bash
set -e

# Test Runner Script
# Runs the full test suite with pytest.
#
# Usage:
#   ./scripts/run-tests.sh              # All tests
#   ./scripts/run-tests.sh -k session   # Filter by keyword
#   ./scripts/run-tests.sh --cov        # With coverage report
#
# Prerequisites: uv sync --group dev

cd "$(dirname "$0")/.."

echo "🧪 Running test suite..."
echo ""

uv run pytest "$@"
