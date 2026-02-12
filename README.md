# Course Materials RAG System

A Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.

## Overview

This application is a full-stack web application that enables users to query course materials and receive intelligent, context-aware responses. It uses ChromaDB for vector storage, Anthropic's Claude for AI generation, and provides a web interface for interaction.


## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- An Anthropic API key (for Claude AI)

## Installation

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Running the Application

### Quick Start

Use the provided shell script:
```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

The application will be available at:
- Web Interface: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## Claude Code Memory Files

Claude Code reads instructions from three memory file locations. Each serves a different scope:

### 1. Project Memory (Shared with team, committed to Git)
```bash
# File: ./CLAUDE.md (root of the project)
# Scope: Everyone who clones this repo gets these instructions
# Example content:
cat CLAUDE.md
```
Use this for project-wide rules like architecture decisions, coding standards, and build commands.

### 2. Local Project Memory (Personal, NOT committed to Git)
```bash
# File: ./CLAUDE.local.md (root of the project)
# Scope: Only YOU on this machine. Add to .gitignore.
# Create it:
echo "# Local Memory" > CLAUDE.local.md
echo "- Always use uv, never pip" >> CLAUDE.local.md
```
Use this for personal preferences that shouldn't affect other developers (e.g., "use vim keybindings", "always use uv").

### 3. User Memory (Global, applies to ALL projects)
```bash
# File: ~/.claude/CLAUDE.md (your home directory)
# Scope: Every project you open with Claude Code on this machine
# Create it:
mkdir -p ~/.claude
echo "# Global Memory" > ~/.claude/CLAUDE.md
echo "- Prefer concise responses" >> ~/.claude/CLAUDE.md
```
Use this for universal preferences like response style, preferred language, or global coding conventions.

