# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in
this repository.

## Project Overview

A single-page portfolio website for architect Eleni Chaziri. Static site (no
frameworks, no build tools) targeting Scandinavian architectural firms.

Design philosophy: Quiet confidence. Simplicity. Architecture first.

## Project Structure

- `images/project-01..04/` — Project images extracted from portfolio PDF
- `assets/` — Source files (portfolio PDF, cover letter PDF)
- `scripts/` — Python/uv tooling for image extraction (gitignored)
- `docs/` — Vision docs

## Colour Palette

- Accent: `#2C5F5C` (deep blue-green)
- Background: `#FFFFFF` (true white)
- Light grey: `#E8E6E3`
- Body text: `#3A3A3A` (graphite)
- Headings: `#1A1A1A` (near-black)

## Development

### Image extraction

Images have been extracted from the @assets/portfolio.pdf using the python script in
@scripts/
