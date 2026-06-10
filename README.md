# Eleni Chaziri — Architect Portfolio

A minimal, single-page portfolio website showcasing architectural projects. Built with
plain HTML, CSS, and vanilla JavaScript — no frameworks, no build tools.

## Preview

Serve locally:

```bash
python3 -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000).

## Structure

```
├── index.html          Single-page site
├── styles.css          Styling (responsive, custom properties)
├── main.js             Expand/collapse interactions
├── images/             Project images (extracted from PDF)
│   ├── project-01/     Xanthi City Pavilion
│   ├── project-02/     Tobacco Warehouse Restoration
│   ├── project-03/     Samothrace Spa Facilities
│   └── project-04/     Historic Building Restoration
├── assets/             Source PDFs
└── scripts/            Image extraction tooling (Python/uv)
```

## Deployment

Static files — deploy anywhere (Netlify, GitHub Pages, Vercel, etc.). No build step
required. Just upload `index.html`, `styles.css`, `main.js`, and the `images/` folder.

## Image Re-extraction

If you need to re-extract images from the portfolio PDF:

```bash
cd scripts
uv run extract_images.py
```

Requires [uv](https://docs.astral.sh/uv/) (installs PyMuPDF automatically).
