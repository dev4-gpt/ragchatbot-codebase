#!/bin/bash

# Code Quality Lint Script - READ-ONLY CHECKS
# Verifies code quality without making changes. Safe for CI/CD.
#
# What it does:
# 1. Runs ruff lint (style, imports, complexity)
# 2. Checks ruff formatting (shows diff)
# 3. Runs mypy type checking (type safety)
#
# Usage: ./scripts/lint.sh
# Prerequisites: uv sync --group dev
# Exit codes: 0 = all checks pass, non-zero = issues found

echo "🔍 Running code quality lint script (read-only checks)..."
echo ""

ERRORS=0

if uv run ruff --version &> /dev/null; then
    echo "1. Running ruff lint..."
    uv run ruff check backend/ main.py || ERRORS=$((ERRORS + 1))

    echo ""
    echo "2. Checking ruff formatting..."
    uv run ruff format --check --diff backend/ main.py || ERRORS=$((ERRORS + 1))
else
    echo "(ruff not found, falling back to flake8 + isort + black)"
    echo "1. Running flake8 linting..."
    uv run flake8 backend/ main.py || ERRORS=$((ERRORS + 1))

    echo ""
    echo "2. Checking import sorting..."
    uv run isort --check-only --diff backend/ main.py || ERRORS=$((ERRORS + 1))

    echo ""
    echo "3. Checking code formatting..."
    uv run black --check --diff backend/ main.py || ERRORS=$((ERRORS + 1))
fi

echo ""
echo "4. Running mypy type checking..."
uv run mypy backend/ main.py --ignore-missing-imports || ERRORS=$((ERRORS + 1))

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All quality checks passed!"
else
    echo "❌ $ERRORS check(s) failed."
    exit 1
fi

echo "Code quality checks completed!"