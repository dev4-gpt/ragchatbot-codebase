#!/bin/bash
set -e

# Full Quality Check Script — Lint + Test in one go
# Runs all quality checks and then the test suite.
#
# Usage: ./scripts/check.sh

echo "========================================="
echo "  Full Quality Check: Lint + Test"
echo "========================================="
echo ""

# Step 1: Lint
echo "── Step 1/2: Lint ──"
bash "$(dirname "$0")/lint.sh"
LINT_EXIT=$?

echo ""

# Step 2: Tests
echo "── Step 2/2: Tests ──"
cd "$(dirname "$0")/.."
uv run pytest
TEST_EXIT=$?

echo ""
echo "========================================="
if [ $LINT_EXIT -eq 0 ] && [ $TEST_EXIT -eq 0 ]; then
    echo "  ✅ All checks passed!"
else
    echo "  ❌ Some checks failed."
    exit 1
fi
