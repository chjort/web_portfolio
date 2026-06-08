# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A personal web portfolio site. Python 3.13 project managed with uv.

## Development Setup

```bash
uv sync          # install dependencies
uv run <script>  # run a script
```

## Project Structure

- `assets/` — Static files (portfolio PDF, cover letter PDF)
- `pyproject.toml` — Project metadata and dependencies (uv-managed)
- `.python-version` — Pins Python 3.13
