# Portfolio Site — Design Spec

**Subject:** Architectural portfolio website for Eleni Chaziri.
**Date:** 2026-06-13.
**Status:** Approved design, ready for implementation planning.

## 1. Goals & constraints

A static, multi-page portfolio website targeting Scandinavian architectural
firms, particularly in Copenhagen. The site must communicate clarity,
analytical thinking, technical competence, and design maturity. Design
philosophy: quiet confidence, simplicity, architecture first.

**Hard constraints**

- Pure static HTML and CSS. No JavaScript frameworks. No runtime build step.
- No third-party trackers, analytics, or font CDNs.
- Hosted on GitHub Pages under a project subpath. **All paths must be
  relative** (no leading `/`); no hard-coded absolute URLs.
- One Python image-optimization script in `scripts/` is the only "build"; it
  is run manually when source images change and its output is committed.

**Out of scope for this build**

- Multilingual UI. The CV mentions EN/IT/GR fluency but the site ships in
  English only. A language switcher is a clean future addition; the
  architecture should not preclude it.
- Contact form, mailing list, blog, CMS.
- A "Download CV" link. The site replaces the CV.
- Lightbox / modal viewers for drawings.

## 2. Information architecture

```
/
├── index.html                       Landing
├── about.html                       Profile, CV content, contact (#contact)
└── projects/
    ├── 01-xanthi-pavilion.html
    ├── 02-tobacco-warehouse.html
    ├── 03-therma-spa.html
    └── 04-historic-restoration.html
```

**Header (every page)**

- Wordmark "Chaziri Eleni" — links to `index.html`.
- Nav: `Work` (→ `index.html#work`) · `About` (→ `about.html`).
- No "Contact" link. Sticky, hairline divider only, no shadow.

**No footer on any page.** Contact info appears only at the bottom of the
About page.

**Index page sequence**

1. Hero — type-only, vertical hairline (1px, accent colour) running from the
   top of the hero to ~75% of viewport height. Wordmark sits in the lower
   third just left of where the hairline ends. Three lines of type:
   - "Chaziri Eleni" — Bold, `letter-spacing: 0.4em`.
   - "Architect's Portfolio" — Regular, smaller, accent colour.
   - "2021–2025" — Light, smaller still.
2. Statement — 2 sentences, max-width 50ch:
   > "An architect working across public space, restoration, and building
   > design — from concept through detailed development and delivery. Based in
   > Thessaloniki, available internationally."
3. Selected Work (`id="work"`) — a 4-card grid mirroring the PDF index page.
   Each card: hero image, project number (Light), project title (Regular),
   centred. Whole card links to the project page.
4. About teaser — 2–3 lines + "Read more →" link to `about.html`.

**No contact strip on the index.** Contact lives only on About.

## 3. Visual system

### Colour tokens (CSS custom properties on `:root`)

```css
--ink:    #1A1A1A;   /* headings */
--body:   #3A3A3A;   /* body text */
--accent: #2C5F5C;   /* deep blue-green; links, hairlines, project numerals */
--bg:     #FFFFFF;   /* background */
--mute:   #E8E6E3;   /* light grey; section dividers, drawing backgrounds */
--rule:   #D6D4D1;   /* hairlines, table borders */
```

Contrast: `--body` on `--bg` = 10.4:1 (AAA). `--accent` on `--bg` = 7.0:1
(AAA for normal text).

### Typography

Family: **Jost** (self-hosted .woff2 in `styles/fonts/`), as a
freely-licensed stand-in for Century Gothic. Weights 300, 400, 700.

Stack: `'Jost', 'Century Gothic', 'CenturyGothic', 'URW Gothic', sans-serif`.
Visitors with Century Gothic installed locally see it natively; everyone
else gets Jost.

Weight assignments:

- **Bold (700)** — hero, page headings, project titles, link active states.
- **Regular (400)** — body, nav, section headings, project subtitles.
- **Light (300)** — footnotes, captions, metadata, project numerals.

Type scale (desktop, modular 1.25):

| Role            | Size      | Weight  | Notes                                    |
|-----------------|-----------|---------|------------------------------------------|
| Hero wordmark   | 3.5rem    | 700     | `letter-spacing: 0.4em`, uppercase       |
| Page title (H1) | 2rem      | 700     | section anchor, hairline rule beneath    |
| Section (H2)    | 1.25rem   | 400     |                                          |
| Body            | 1rem      | 400     | `line-height: 1.65`, max-width 62ch      |
| Caption / label | 0.8125rem | 300     | `letter-spacing: 0.08em`, uppercase      |

Project numerals (e.g., "01") use Light, oversized, accent colour.

### Spacing & layout

- 8px base unit.
- Section vertical rhythm: 6rem desktop, 3rem mobile between major blocks.
- Side gutters: `clamp(1.5rem, 5vw, 6rem)`.
- Hairlines: 1px, `--rule` (or `--accent` for emphasis).
- Page max-width: 1440px (`.frame` wrapper).

### Layout primitives (defined once in `project.css`)

- `.frame` — page wrapper, max-width 1440px, fluid gutters.
- `.spread` — vertical block; defaults to single column.
- `.spread--two-up` — two equal columns, CSS Grid `repeat(2, 1fr)` with gutter.
- `.spread--three-up` — three equal columns.
- `.spread--text-image` — text 40% / image 60%, stacks on mobile.
- `.spread--asymmetric` — text on one side, stacked image group on the other.
- `.spread--text-only` — narrow centred text column (max-width 62ch).
- `.spread--full` — single full-width image.
- `.caption` — small Light uppercase label beneath a drawing/image.
- `.drawing` — wraps technical drawings; sits on `--mute` background with
  generous internal padding so plans/sections do not compete with renders.

Per-project pages compose these primitives in HTML; no per-page CSS files.

### Animation

- Hover: 200ms opacity fade on links/nav; 300ms `translateY(-2px)` on project
  cards.
- No scroll-triggered animation, parallax, carousels, or page transitions.
- `@media (prefers-reduced-motion: reduce)` disables the hover transforms.

### Responsive breakpoints (mobile-first)

- Base: single column everywhere.
- `@media (min-width: 600px)` — two-up grids appear.
- `@media (min-width: 1000px)` — full grid behaviour, side gutters open up.
- No fixed pixel widths in content; `clamp()` and `fr` units throughout.

## 4. Project pages

Each project page is **layout-faithful to its PDF spreads**, not a generic
gallery template. Same compositional logic, adapted to vertical scroll.

### Shared scaffold

1. **Project header**
   - Project number (Light, large, accent colour).
   - Title (Bold).
   - One-line subtitle / location / year (Regular, muted).
   - Hairline rule beneath.
2. **Spread sequence** — see per-project layout maps below.
3. **"Next project →"** link at the bottom (cyclic: 04 → 01).

### Image weighting rules

- A heavy renders block is never adjacent to another heavy renders block
  without a lighter element between (drawings, plans, sections, whitespace).
- Plans, sections, diagrams sit on `--mute` (light grey) with generous
  internal padding.
- Hairline rules separate spreads — no thick dividers.
- Each project page opens and closes on text or whitespace, not a heavy
  render.

### Per-project layout maps

All image references use the `images/web/project-XX/` optimized variants.
**`project-02/image-07.jpeg` is excluded from the site** per the vision doc.

**01 — Xanthi City Pavilion** (11 images)

1. Project header.
2. `.spread--text-only` — opening narrative paragraphs (PDF page 3 left
   column).
3. `.spread--full` — strongest exterior render (image-01 or equivalent hero).
4. `.spread--two-up` — two interior renders (e.g., images-02, 03).
5. `.spread--asymmetric` — three small volume sketches stacked, plus the
   long section drawing.
6. `.spread--three-up` — three plan drawings side by side (PDF page 4).
7. `.spread--text-image` — "uses." narrative + masterplan diagram (PDF
   page 4 right).
8. `.spread--two-up` — two short elevation/section drawings.

**02 — Tobacco Warehouse** (27 images, image-07 excluded)

1. Project header.
2. `.spread--text-only` — historical overview (PDF page 5).
3. `.spread--asymmetric` — urban context map + existing-condition facade
   photogrammetry drawings.
4. `.spread--two-up` — existing condition drawings (PDF page 5 right).
5. `.spread--asymmetric` — analysis text + facade damage-mapping (PDF
   page 6).
6. `.spread--two-up` — material and preservation-status drawings (PDF
   page 7).
7. `.spread--text-only` — proposal description (PDF page 8).
8. `.spread--full` — restoration plan and section drawings.
9. `.spread--two-up` × 2 — interior renders of restored warehouse.
10. `.spread--asymmetric` — proposal description + new building elevations.
11. `.spread--full` — exterior renders of new addition (PDF page 10).

**03 — Therma Spa** (10 images)

1. Project header.
2. `.spread--text-only` — opening narrative (PDF page 11).
3. `.spread--text-image` — composite concept + main section drawing.
4. `.spread--two-up` — two sections side by side.
5. `.spread--two-up` — two renders side by side.
6. `.spread--full` — strongest exterior render.
7. `.spread--two-up` — landscape views.

**04 — Historic Restoration** (12 images)

1. Project header.
2. `.spread--text-only` — principles of intervention (PDF page 13).
3. `.spread--text-image` — intervention principles + restored facade
   elevation.
4. `.spread--two-up` — decorative pattern study (pattern completion +
   original witnesses).
5. `.spread--asymmetric` — interior renders + new-uses diagrams.
6. `.spread--text-image` — building program + restored exterior elevations.
7. `.spread--two-up` — final interior renders.

These maps are the source of truth for spread order and primitive choice.
When implementing, cross-reference the corresponding PDF page for the visual
hierarchy and proportions of each spread; the maps tell *what* and *in what
order*, the PDF tells *how it should look on the page*.

## 5. About page

`about.html`. Three blocks.

1. **Page header** — "About" (Bold, H1), hairline rule.
2. **Profile statement** — 2–3 sentences, factual third-person:
   > "Architect based in Thessaloniki, working across public space,
   > restoration, and building design. Member of the Technical Chamber of
   > Greece. Currently a junior architect at OFFICE25ARCHITECTS."
3. **Two-column block** (stacks on mobile):
   - **Left — Experience & Education**
     - Experience
       - 09.2023 – present · Junior Architect, OFFICE25ARCHITECTS · Thessaloniki, Greece
       - 07.2022 – 09.2022 · Intern, Akis Firoglanis Technical Office · Rhodes, Greece
     - Education
       - 2017 – 2024 · Democritus University of Thrace · Architectural Engineering Department
     - Seminars
       - 14.10.2020 · GSD1x: The Architectural Imagination · HarvardX
   - **Right — Skills & Languages**
     - Technical: ArchiCAD · AutoCAD · Revit · Lumion · Twinmotion · SketchUp · 3dsMax · Photoshop · InDesign · Metashape · Office365. Rendered as a flat tag list (Light, small, hairline-bordered chips). **No dot-density meter.**
     - Soft skills: short bulleted list — concept development, technical attention to detail, collaboration, presentation, adaptability, time management, historical/cultural research.
     - Languages: English — fluent (IELTS 7.5, 2024 · C2 EDI, 2016) · Italian — very good (C1 KPG) · Greek — native.
4. **Hairline rule, then Contact block** (`id="contact"`):
   - Email — Bold, accent colour, `mailto:` link. **Placeholder pending real value.**
   - Phone — Regular, `tel:` link. **Placeholder pending real value.**
   - Location: Thessaloniki, Greece.

## 6. Image pipeline

**Source:** `images/project-XX/<name>.<ext>` — already extracted from the
PDF; never modified.

**Generated:** `images/web/project-XX/<name>-{1600,800,400}.jpg` —
optimized JPEG variants. Committed to git so GitHub Pages serves them
directly.

**Script:** `scripts/optimize_images.py`.

- Reads from `images/project-XX/`, writes to `images/web/project-XX/`.
- For each source: produce 1600w, 800w, 400w JPEGs at quality 82, progressive,
  sRGB; strip EXIF.
- Uses Pillow via the existing `scripts/pyproject.toml` uv environment.
- **Idempotent:** skips outputs whose mtime is newer than the source mtime.
- **Excludes** `project-02/image-07.jpeg` explicitly with a logged note.
- Run manually: `cd scripts && uv run optimize_images.py`.

**HTML usage**

- `<img>` uses `srcset` + `sizes` for responsive selection.
- `loading="lazy"` on every below-the-fold image.
- Hero / above-the-fold images get `fetchpriority="high"` and no lazy-load.
- Every `<img>` has `width` and `height` attributes set, to prevent layout
  shift. The script writes these dimensions into a `images/web/_manifest.json`
  used during HTML authoring (the running site does not read it).

## 7. Accessibility

- Semantic HTML: `<main>`, `<article>` per project, `<nav>`, ordered
  `<h1>`–`<h3>`.
- Every image has meaningful `alt` text (drawn from the PDF caption when
  available, otherwise descriptive); decorative-only images use `alt=""`.
- `:focus-visible` outline: 1px `--accent`, 2px offset, on every link and
  interactive element.
- `<html lang="en">` everywhere.
- `prefers-reduced-motion: reduce` disables hover transforms.
- Tab order is natural reading order; project cards are reachable by keyboard.

## 8. Repository changes summary

- **Add:**
  - `index.html`, `about.html`.
  - `projects/01-xanthi-pavilion.html`, `02-tobacco-warehouse.html`, `03-therma-spa.html`, `04-historic-restoration.html`.
  - `styles/base.css`, `styles/site.css`, `styles/project.css`.
  - `styles/fonts/jost-{300,400,700}.woff2` — Jost is licensed under the SIL Open Font License 1.1. Download the .woff2 files from the official source (https://indestructibletype.com/Jost or fonts.google.com), self-host, and include the license as `styles/fonts/OFL.txt`. **Do not** link to Google Fonts at runtime.
  - `scripts/optimize_images.py` plus its dependency entry in `scripts/pyproject.toml`.
  - `images/web/project-01..04/` — generated output, committed.
  - `images/web/_manifest.json` — image dimensions, committed.
- **Modify:**
  - `CLAUDE.md` — replace the "single-page" line with a description of the
    multi-page structure and the relative-paths convention.
- **Untouched:**
  - `assets/`, `docs/vision.md`, `images/project-XX/` originals.

## 9. Acceptance criteria

The site is "done" when, on a clean clone:

1. Opening `index.html` directly in a browser (no server) renders the site
   correctly with all images, fonts, and styles loaded — confirms relative
   paths work.
2. Header nav (`Work`, `About`) navigates correctly across all six pages.
3. Each of the four project pages displays every image listed in its layout
   map, in the documented order, with captions where present in the PDF.
   `project-02/image-07.jpeg` is not present anywhere on the site.
4. About page contains all CV content listed in §5; contact block has clearly
   marked placeholders for email and phone.
5. Lighthouse (or equivalent) reports no accessibility errors. Colour contrast
   passes AAA for body text and AA-large for accent text.
6. No layout shift on image load (CLS ≈ 0).
7. Total page weight on the heaviest project page (project-02, 27 images)
   stays under 3 MB on initial load with lazy-loading active.
8. Site renders cleanly at 360px (small phone), 768px (tablet), and 1440px
   (desktop) widths with no horizontal scroll.
