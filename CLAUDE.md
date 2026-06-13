# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in
this repository.

## Project Overview

A static portfolio website for architect Eleni Chaziri. Multi-page (index + about +
four project pages), hosted on GitHub Pages under a project subpath. No frameworks,
no JavaScript, no runtime build tools.

Design philosophy: Quiet confidence. Simplicity. Architecture first.

Spec: `docs/superpowers/specs/2026-06-13-portfolio-site-design.md`.
Plan: `docs/superpowers/plans/2026-06-13-portfolio-site.md`.

## Project Structure

- `index.html` — landing page.
- `about.html` — profile, CV content, contact (`#contact` anchor).
- `projects/0X-*.html` — one page per project.
- `styles/base.css` — design tokens, reset, type scale, layout primitives.
- `styles/site.css` — header, nav, index page, about page.
- `styles/project.css` — spread refinements, project header, captions.
- `styles/fonts/` — self-hosted Jost (.woff2) under SIL OFL.
- `images/project-0X/` — image originals extracted from the portfolio PDF (untouched).
- `images/web/project-0X/` — generated 1600/800/400-wide JPEG variants (committed).
- `images/web/_manifest.json` — intrinsic source dimensions, used during HTML authoring.
- `assets/` — source PDFs (portfolio, CV).
- `scripts/` — Python tooling (uv-managed): `extract_images.py`, `optimize_images.py`.
- `docs/` — vision, specs, plans.

## Path conventions

The site is hosted on GitHub Pages under a project subpath (e.g.,
`username.github.io/web_portfolio/`). To keep the site portable and to keep
`file://` previews working without a server:

- Use **relative paths** in every `<a href>`, `<link href>`, and `<img src>`.
- Project pages live one directory deep, so they reference assets with `../`
  (e.g., `../styles/base.css`, `../images/web/project-01/...`).
- Index and about pages live at the root, so they reference assets without a
  prefix (e.g., `styles/base.css`, `images/web/...`).
- Never start a path with `/` and never embed an absolute URL to this site's
  own resources.

## Colour palette

- Accent: `#2C5F5C` (deep blue-green) — links, hairlines, project numerals.
- Background: `#FFFFFF` (true white).
- Light grey: `#E8E6E3` — drawing backgrounds, mute panels.
- Hairline grey: `#D6D4D1`.
- Body text: `#3A3A3A` (graphite).
- Headings: `#1A1A1A` (near-black).

These are exposed as CSS custom properties in `styles/base.css`:
`--accent`, `--bg`, `--mute`, `--rule`, `--body`, `--ink`.

## Typography

- Family: **Jost** (self-hosted .woff2), as a freely-licensed stand-in for Century Gothic.
- Weights: 300 (Light, captions/footnotes), 400 (Regular, body), 700 (Bold, headings).
- Stack: `'Jost', 'Century Gothic', 'CenturyGothic', 'URW Gothic', sans-serif`.

## Image pipeline

Run from the `scripts/` directory whenever images under `images/project-0X/` change:

```
cd scripts/
uv run optimize_images.py
```

The script is idempotent and writes to `images/web/`. Commit the output. The
hard-coded exclusion list in `optimize_images.py` skips
`images/project-02/image-07.jpeg` per the vision doc.

## Development

There is no dev server — open the `.html` files directly in a browser. Validate
with `tidy -q -e <file>` and run Lighthouse audits before committing changes
that affect rendering. Aim for accessibility score 100 and CLS < 0.01.
