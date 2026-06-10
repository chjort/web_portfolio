# Portfolio Website Design Spec

**Author:** Eleni Chaziri  
**Date:** 2026-06-10  
**Status:** Approved

---

## Overview

A single-page, static portfolio website for architect Eleni Chaziri. The site serves
as both a job application tool (sent alongside applications to Scandinavian firms) and
a standalone professional web presence. It communicates clarity, analytical thinking,
technical competence, and design maturity.

**Design philosophy:** Quiet confidence. Simplicity. Architecture first.

---

## Technology

- Plain HTML (`index.html`)
- Plain CSS (`styles.css`)
- Vanilla JavaScript (`main.js`) — expand/collapse interactions only
- No build tools, no frameworks, no dependencies
- Images extracted from the portfolio PDF, stored in `images/`
- Hosting-agnostic (static files, deployable anywhere)

---

## Page Structure

A single scrolling page with three sections:

### 1. Header/Hero

- Typographic only — no hero image
- Name: "Eleni Chaziri"
- Subtitle: "Architect"
- A vertical accent line in deep blue-green (referencing the PDF cover's design)
- Generous whitespace, spaced letter-spacing on the name

### 2. Projects (Vertical Stack)

Four projects, displayed sequentially in a full-width vertical stack. Each project
block contains:

**Collapsed state (default):**
- Large hero image (primary render, up to ~1200px wide)
- Project number + title + location, left-aligned
- 2-3 sentence summary
- "More +" text link to expand

**Expanded state:**
- Hero image remains visible
- Fuller description (design rationale, key moves)
- Additional images in a mixed layout:
  - Full-width for renders and key drawings
  - 2-column pairs for technical drawings, plans, sections
- "Less −" text link to collapse

**Project content:**

**01 — Xanthi City Pavilion**
- Location: Xanthi, Greece
- Summary: A cultural centre in the marketplace area, comprising three volumes
  positioned on the ground level with a third functioning as a bridge. The design
  emphasizes fluidity, transparency of movement, and a central public square with
  an open-air cinema.
- Expanded content: full description of uses (Citizens Service Centre, showrooms,
  catering hall, guest rooms, multi-purpose hall), structural system (composite
  metal beams and HP steel columns in concrete), and claustra cladding system.
- Images: renders, interior views, section drawing, site diagrams, floor plans,
  elevations.

**02 — Restoration of the Tobacco Warehouse, Nestos Street, Xanthi**
- Location: Xanthi, Greece
- Summary: Restoration and adaptive reuse of a heritage-designated tobacco
  warehouse (10.50m × 27m, built for tobacco storage, designated 2011) as a
  digital library and reading room for the local university community.
- Expanded content: historical context, documentation methodology
  (photogrammetry), materials analysis, damage mapping, and the restoration and
  reuse proposal (glass roof replacement, new building addition with metal bridge,
  digital library on upper floors).
- Images: site plan, existing condition facades, damage mapping diagrams,
  material/construction technique drawings, restoration proposal plans, sections,
  interior renders.

**03 — Spa Facilities & Hospitality Areas, Therma, Samothrace**
- Location: Therma, Samothrace, Greece
- Summary: Spa facilities, wellness centre, and hospitality spaces developed
  within the natural landscape. The design uses simple, minimalistic forms,
  tranquil lines, a modular cellular structure, and a progression across multiple
  levels harmonising with the terrain.
- Expanded content: three distinct architectural volumes, each dedicated to a
  specific programmatic function, operating autonomously while forming a unified
  visual and spatial whole.
- Images: renders (multiple landscape views, pool area, interior), site sections.

**04 — Restoration, Redesign & Reuse of Historic Buildings and Sites**
- Location: Greece
- Summary: Adaptive reuse of a historic building guided by principles of selective
  reversal of alterations, historical conservation, targeted restoration, balanced
  interventions, and modern adaptation. The building is repurposed as a functional
  resource centre for the academic community.
- Expanded content: intervention principles, building program (ground floor:
  printing/storage/cafeteria; first floor: library/study area; attic: design
  studios), facade restoration approach with pattern completion.
- Images: facade restoration drawing, original witness patterns, interior renders,
  floor plans, use diagrams.

### 3. About + Contact

- Heading: "Eleni Chaziri"
- First-person bio (3-4 sentences):
  - Architect with professional experience at Office25Architects
  - Work spanning residential, commercial, and mixed-use developments
  - Skills in detailed architectural drawings, concept development, permit
    submissions, and project coordination
  - Interest in sustainability, human connection, and cultural relevance
- Skills: ArchiCAD, AutoCAD, Revit, Adobe Suite
- Languages: English, Italian, Greek
- Contact: email as a mailto link (elenihaziri@gmail.com)

### Footer

- "© Eleni Chaziri 2025" in small type
- No social links

---

## Visual Language

### Colour Palette

| Role | Colour | Hex (approximate) |
|------|--------|-------------------|
| Accent | Deep blue-green | `#2C5F5C` |
| Background | Soft white | `#F8F7F5` |
| Dividers/secondary | Light grey | `#E8E6E3` |
| Body text | Graphite grey | `#3A3A3A` |
| Headings | Near-black | `#1A1A1A` |

### Typography

- Sans-serif family (Inter, Instrument Sans, or similar geometric-but-warm typeface)
- Headings: medium/semi-bold weight, generous letter-spacing
- Body: regular/light weight, comfortable reading size (~16-18px)
- Large type hierarchy: project titles prominent, body text readable

### Spacing & Rhythm

- 120–160px vertical whitespace between projects
- Content constrained to ~720–900px for text
- Images allowed up to ~1200px wide
- Asymmetric layout moments (text left-aligned, images occasionally breaking grid)

### Animation

- Smooth expand/collapse (height + opacity transition)
- Optional subtle fade-in on scroll for project sections
- No parallax, no dramatic reveals

---

## Responsive Behaviour

### Desktop (1200px+)
- Text content ~900px, images up to ~1200px
- Side-by-side image pairs in expanded view
- Generous whitespace

### Tablet (768–1199px)
- Content fills more of viewport with comfortable margins
- Image pairs remain side-by-side but smaller
- Slightly tighter spacing

### Mobile (< 768px)
- Single column throughout
- Image pairs stack vertically
- Hero images full-width or near-full-width
- Typography scales down proportionally
- Reduced vertical spacing between projects
- Expand/collapse unchanged

---

## File Structure

```
web_portfolio/
├── index.html
├── styles.css
├── main.js
├── images/
│   ├── project-01/
│   │   ├── hero.jpg
│   │   ├── section.jpg
│   │   ├── plan-ground.jpg
│   │   ├── ...
│   ├── project-02/
│   │   ├── hero.jpg
│   │   ├── ...
│   ├── project-03/
│   │   ├── ...
│   └── project-04/
│       ├── ...
├── assets/
│   ├── portfolio.pdf
│   └── coverletter.pdf
└── docs/
    └── vision.md
```

---

## Out of Scope

- No CMS or admin panel
- No contact form (email link only)
- No blog or news section
- No multi-language versions of the site (languages listed as a skill only)
- No custom domain setup (to be handled separately later)
- No analytics (can be added later)
- No SEO optimisation beyond basic meta tags
