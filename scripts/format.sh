#!/bin/bash
set -e

# Code Quality Format Script - MODIFIES FILES
# Formats code using ruff (primary) with black+isort fallback.
#
# What it does:
# 1. Auto-fixes lint issues + sorts imports (ruff check --fix)
# 2. Formats code style (ruff format)
# 3. Reports remaining lint issues
#
# Usage: ./scripts/format.sh
# Prerequisites: uv sync --group dev

echo "🔧 Running code quality format script (will modify files)..."
echo ""

if uv run ruff --version &> /dev/null; then
    echo "1. Auto-fixing lint issues + sorting imports with ruff..."
    uv run ruff check --fix backend/ main.py 2>/dev/null || true

    echo "2. Formatting code with ruff..."
    uv run ruff format backend/ main.py

    echo ""
    echo "3. Remaining lint issues (if any):"
    uv run ruff check backend/ main.py || true
else
    echo "(ruff not found, falling back to isort + black + flake8)"
    echo "1. Sorting imports with isort..."
    uv run isort backend/ main.py

    echo "2. Formatting code with Black..."
    uv run black backend/ main.py

    echo "3. Running flake8 linting..."
    uv run flake8 backend/ main.py || true
fi

echo ""
echo "✅ Code formatting complete!"