# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in
this repository.

## Project Overview

A single-page portfolio website for architect Eleni Chaziri. Static site (no
frameworks, no build tools) targeting Scandinavian architectural firms.

Design philosophy: Quiet confidence. Simplicity. Architecture first.

## Project Structure

- `index.html` — Single-page site (header, 4 projects, about, footer)
- `styles.css` — All styling (custom properties, responsive breakpoints)
- `main.js` — Expand/collapse interaction for project details
- `images/project-01..04/` — Project images extracted from portfolio PDF
- `assets/` — Source files (portfolio PDF, cover letter PDF)
- `scripts/` — Python/uv tooling for image extraction (gitignored)
- `docs/` — Vision doc, design spec, implementation plan

## Key Conventions

- Plain HTML/CSS/JS — no frameworks, no build step, no dependencies
- BEM naming for CSS classes (e.g. `.project__title`, `.header__accent`)
- CSS custom properties for colours, typography, spacing
- Semantic HTML with accessibility attributes (aria-expanded, aria-controls)
- Images named descriptively (hero.jpg, section.jpg, facade-east.jpg)

## Colour Palette

- Accent: `#2C5F5C` (deep blue-green)
- Background: `#F8F7F5` (soft white)
- Light grey: `#E8E6E3`
- Body text: `#3A3A3A` (graphite)
- Headings: `#1A1A1A` (near-black)

## Development

Serve locally:
```
python3 -m http.server 8000
```

Re-extract images from PDF:
```
cd scripts && uv run extract_images.py
```
