# Portfolio Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page static portfolio website for architect Eleni Chaziri with four expandable project sections, an about section, and minimal styling.

**Architecture:** One `index.html` file with semantic sections, one `styles.css` for all visual styling, one `main.js` for expand/collapse interaction. Images stored in `images/project-NN/` folders. No build tools or frameworks.

**Tech Stack:** HTML5, CSS3 (custom properties, flexbox, grid), vanilla JavaScript (ES6+)

---

## File Structure

```
web_portfolio/
├── index.html          — All page content and structure
├── styles.css          — All visual styling (palette, typography, layout, responsive)
├── main.js             — Expand/collapse interaction logic
└── images/
    ├── project-01/     — Xanthi City Pavilion images
    │   ├── hero.jpg
    │   ├── interior.jpg
    │   ├── section.jpg
    │   ├── diagrams.jpg
    │   ├── plans.jpg
    │   └── elevations.jpg
    ├── project-02/     — Tobacco Warehouse images
    │   ├── hero.jpg
    │   ├── site-plan.jpg
    │   ├── facade-east.jpg
    │   ├── facade-south.jpg
    │   ├── damage-mapping.jpg
    │   ├── materials.jpg
    │   ├── sections.jpg
    │   ├── restoration-plans.jpg
    │   ├── restoration-sections.jpg
    │   ├── proposal-description.jpg
    │   └── interiors.jpg
    ├── project-03/     — Samothrace Spa images
    │   ├── hero.jpg
    │   ├── render-landscape.jpg
    │   ├── section-site.jpg
    │   ├── renders-views.jpg
    │   └── sections-full.jpg
    └── project-04/     — Historic Restoration images
        ├── hero.jpg
        ├── facade-restoration.jpg
        ├── patterns.jpg
        ├── interiors.jpg
        ├── floor-plans.jpg
        └── use-diagrams.jpg
```

---

### Task 1: Extract Images from Portfolio PDF

**Files:**
- Create: `images/project-01/hero.jpg` (and all image files listed in file structure above)

This task extracts all project images from the portfolio PDF. Each page spread contains
images that need to be extracted as individual files.

- [ ] **Step 1: Install extraction tool**

Run:
```bash
pip install pymupdf
```
Expected: successful installation

- [ ] **Step 2: Create extraction script**

Create file `scripts/extract_images.py`:

```python
#!/usr/bin/env python3
"""Extract images from portfolio PDF into project folders."""

import fitz  # PyMuPDF
import os
from pathlib import Path

PDF_PATH = "assets/portfolio.pdf"
OUTPUT_DIR = "images"

# Page ranges per project (0-indexed)
# Page 0: cover
# Page 1: table of contents
# Pages 2-3: Project 01 (Xanthi City Pavilion)
# Pages 4-5: Project 02 (Tobacco Warehouse) - documentation
# Pages 6-7: Project 02 - analysis & materials
# Pages 8-9: Project 02 - restoration proposal & description
# Pages 10-11: Project 03 (Samothrace Spa)
# Pages 12-13: Project 04 (Historic Restoration)

PROJECT_PAGES = {
    "project-01": [2, 3],
    "project-02": [4, 5, 6, 7, 8, 9],
    "project-03": [10, 11],
    "project-04": [12, 13],
}


def extract_images():
    doc = fitz.open(PDF_PATH)

    for project, pages in PROJECT_PAGES.items():
        project_dir = Path(OUTPUT_DIR) / project
        project_dir.mkdir(parents=True, exist_ok=True)

        img_count = 0
        for page_num in pages:
            page = doc[page_num]
            images = page.get_images(full=True)

            for img_index, img_info in enumerate(images):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # Skip very small images (likely UI elements)
                if len(image_bytes) < 10000:
                    continue

                img_count += 1
                filename = f"image-{img_count:02d}.{image_ext}"
                filepath = project_dir / filename

                with open(filepath, "wb") as f:
                    f.write(image_bytes)

                print(f"  Extracted: {filepath} ({len(image_bytes)} bytes)")

    doc.close()
    print("\nDone. Review images/ and rename files to match their content.")
    print("Expected names: hero.jpg, section.jpg, plans.jpg, etc.")


if __name__ == "__main__":
    extract_images()
```

- [ ] **Step 3: Run the extraction script**

Run:
```bash
python scripts/extract_images.py
```
Expected: Images extracted into `images/project-01/`, `images/project-02/`, etc.

- [ ] **Step 4: Review and rename extracted images**

Manually review extracted images and rename them to descriptive names matching the file
structure above. The first/largest render for each project becomes `hero.jpg`. Technical
drawings, sections, plans get descriptive names.

- [ ] **Step 5: Commit extracted images**

```bash
git add images/
git commit -m "feat: extract project images from portfolio PDF"
```

---

### Task 2: HTML Structure

**Files:**
- Create: `index.html`

- [ ] **Step 1: Create `index.html` with full page structure**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Eleni Chaziri — Architect. Portfolio showcasing public spaces, restoration, and building design.">
    <title>Eleni Chaziri — Architect</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>

    <!-- Header -->
    <header class="header">
        <div class="header__content">
            <h1 class="header__name">Eleni Chaziri</h1>
            <p class="header__title">Architect</p>
        </div>
        <div class="header__accent"></div>
    </header>

    <!-- Projects -->
    <main class="projects">

        <!-- Project 01 -->
        <article class="project" data-project="01">
            <div class="project__hero">
                <img src="images/project-01/hero.jpg" alt="Xanthi City Pavilion — exterior render showing three connected volumes around a public square" loading="lazy">
            </div>
            <div class="project__info">
                <span class="project__number">01</span>
                <h2 class="project__title">Xanthi City Pavilion</h2>
                <p class="project__location">Xanthi, Greece</p>
            </div>
            <p class="project__summary">
                A cultural centre in the marketplace area of Xanthi, comprising three volumes — two on the ground level aligned with the topography, and a third functioning as a bridge. The design emphasizes fluidity, transparency of movement, and a central public square with an open-air cinema.
            </p>
            <button class="project__toggle" aria-expanded="false" aria-controls="project-01-details">
                More +
            </button>
            <div class="project__details" id="project-01-details" hidden>
                <div class="project__description">
                    <p>The proposal aims to rejuvenate the area through the establishment of a Cultural Centre, envisioned as an attraction for diverse age groups and a catalyst for economic, touristic and cultural development.</p>
                    <p>The design and arrangement of the volumes emphasize fluidity in all directions. Transparency of movement within and through the buildings was central to the concept, creating a clear and accessible flow across the site. A covered walkway extends from west to east, linking the plaza to a large green area across from the university campus.</p>
                    <p>The ground floor includes a Citizens Service Centre, information points, internet access zones, offices, a city exhibition, showrooms, and a small bar. The next level features a catering hall. The northern section houses showrooms, pavilions, adaptable workshops and studios, a café, and support spaces. The third volume is dedicated to guest rooms, baths, and a multi-purpose hall connected by an outdoor bridge.</p>
                    <p>The concrete structure is enclosed in a flat framework — a claustra — with both transparent and semi-transparent glass cladding for visual interest and light control. The building is constructed with a composite system featuring metal beams and HP steel bearing columns encased in concrete.</p>
                </div>
                <div class="project__gallery">
                    <figure class="project__image project__image--full">
                        <img src="images/project-01/interior.jpg" alt="Interior view showing open-plan space with natural light" loading="lazy">
                    </figure>
                    <div class="project__image-pair">
                        <figure class="project__image">
                            <img src="images/project-01/section.jpg" alt="Building section showing level changes and bridge volume" loading="lazy">
                        </figure>
                        <figure class="project__image">
                            <img src="images/project-01/diagrams.jpg" alt="Site diagrams showing circulation and massing" loading="lazy">
                        </figure>
                    </div>
                    <div class="project__image-pair">
                        <figure class="project__image">
                            <img src="images/project-01/plans.jpg" alt="Floor plans showing programme distribution" loading="lazy">
                        </figure>
                        <figure class="project__image">
                            <img src="images/project-01/elevations.jpg" alt="Building elevations" loading="lazy">
                        </figure>
                    </div>
                </div>
            </div>
        </article>

        <!-- Project 02 -->
        <article class="project" data-project="02">
            <div class="project__hero">
                <img src="images/project-02/hero.jpg" alt="Tobacco Warehouse restoration — exterior view of the heritage building with new glass roof" loading="lazy">
            </div>
            <div class="project__info">
                <span class="project__number">02</span>
                <h2 class="project__title">Restoration of the Tobacco Warehouse</h2>
                <p class="project__location">Nestos Street, Xanthi, Greece</p>
            </div>
            <p class="project__summary">
                Restoration and adaptive reuse of a heritage-designated tobacco warehouse as a digital library and reading room. The thesis documents the building through photogrammetry, analyses its condition, and proposes its transformation into a resource for the local university community.
            </p>
            <button class="project__toggle" aria-expanded="false" aria-controls="project-02-details">
                More +
            </button>
            <div class="project__details" id="project-02-details" hidden>
                <div class="project__description">
                    <p>The tobacco warehouse is located in the centre of Xanthi — a small, rectangular building (10.50m × 27m) designated a heritage monument in 2011. Despite being a single structure, it functioned as two separate spaces, with a main level at +1.30m, a semi-basement at -2.00m, and a now-collapsed mezzanine.</p>
                    <p>Research revealed that the local community undervalues the cultural significance of the tobacco warehouses. This realization inspired the proposal for a Digital Library and Reading Room to support Xanthi's university students and enrich the area's cultural fabric.</p>
                    <p>The restoration replaces the old roof with a glass roof raised by 80 cm, covered with movable shading panels supported by metal frames. The main entrance is on the southern facade at +1.30m. The western section houses an exhibition space and multipurpose hall. The basement level houses special collections, a reading room, and storage.</p>
                    <p>A new building addition connects to the warehouse via a metal bridge — consisting of a ground floor with administration offices and a two-story volume housing the digital library-reading room. Facades are simple, using vertical blinds for controlled shading.</p>
                </div>
                <div class="project__gallery">
                    <figure class="project__image project__image--full">
                        <img src="images/project-02/site-plan.jpg" alt="Site plan showing warehouse location in urban context" loading="lazy">
                    </figure>
                    <div class="project__image-pair">
                        <figure class="project__image">
                            <img src="images/project-02/facade-east.jpg" alt="East facade elevation with existing condition documentation" loading="lazy">
                        </figure>
                        <figure class="project__image">
                            <img src="images/project-02/facade-south.jpg" alt="South facade elevation" loading="lazy">
                        </figure>
                    </div>
                    <figure class="project__image project__image--full">
                        <img src="images/project-02/damage-mapping.jpg" alt="Facade damage mapping showing deterioration types" loading="lazy">
                    </figure>
                    <div class="project__image-pair">
                        <figure class="project__image">
                            <img src="images/project-02/materials.jpg" alt="Material and construction technique recording" loading="lazy">
                        </figure>
                        <figure class="project__image">
                            <img src="images/project-02/sections.jpg" alt="Building sections showing existing condition" loading="lazy">
                        </figure>
                    </div>
                    <figure class="project__image project__image--full">
                        <img src="images/project-02/restoration-plans.jpg" alt="Restoration proposal floor plans" loading="lazy">
                    </figure>
                    <figure class="project__image project__image--full">
                        <img src="images/project-02/restoration-sections.jpg" alt="Restoration proposal sections" loading="lazy">
                    </figure>
                    <figure class="project__image project__image--full">
                        <img src="images/project-02/proposal-description.jpg" alt="Proposal description with uses and elevations" loading="lazy">
                    </figure>
                    <div class="project__image-pair">
                        <figure class="project__image">
                            <img src="images/project-02/interiors.jpg" alt="Interior renders of restored library spaces" loading="lazy">
                        </figure>
                    </div>
                </div>
            </div>
        </article>

        <!-- Project 03 -->
        <article class="project" data-project="03">
            <div class="project__hero">
                <img src="images/project-03/hero.jpg" alt="Spa facilities in Therma, Samothrace — render showing volumes integrated into hillside landscape" loading="lazy">
            </div>
            <div class="project__info">
                <span class="project__number">03</span>
                <h2 class="project__title">Spa Facilities & Hospitality Areas</h2>
                <p class="project__location">Therma, Samothrace, Greece</p>
            </div>
            <p class="project__summary">
                Spa facilities, a wellness centre, and hospitality spaces developed within the natural landscape of Therma. The design uses simple, minimalistic forms, tranquil lines, and a modular cellular structure progressing across multiple levels to harmonise with the terrain.
            </p>
            <button class="project__toggle" aria-expanded="false" aria-controls="project-03-details">
                More +
            </button>
            <div class="project__details" id="project-03-details" hidden>
                <div class="project__description">
                    <p>The composite concept was carefully developed within the natural landscape of Therma, Samothrace, with an emphasis on respecting and enhancing the site's unique character.</p>
                    <p>Extensive research and analysis of the area informed key design objectives: the use of simple, minimalistic forms, tranquil lines, a modular cellular structure, and a progression across multiple levels. These guiding principles inspired the creation of spa facilities, a wellness centre, and hospitality spaces that blend harmoniously with the natural terrain and atmosphere.</p>
                    <p>The facilities are organized into three distinct architectural volumes, each dedicated to a specific programmatic function. This arrangement allows each volume to operate autonomously, ensuring efficient functionality, while the unified design language creates a cohesive whole that is visually and spatially integrated.</p>
                    <p>The result is an architectural composition that balances independence and unity, seamlessly connecting the building's uses to both the surrounding environment and to one another.</p>
                </div>
                <div class="project__gallery">
                    <figure class="project__image project__image--full">
                        <img src="images/project-03/render-landscape.jpg" alt="Landscape view showing buildings stepping down the hillside" loading="lazy">
                    </figure>
                    <figure class="project__image project__image--full">
                        <img src="images/project-03/section-site.jpg" alt="Site section showing how volumes follow the terrain" loading="lazy">
                    </figure>
                    <div class="project__image-pair">
                        <figure class="project__image">
                            <img src="images/project-03/renders-views.jpg" alt="Multiple views showing pool area and interior spaces" loading="lazy">
                        </figure>
                        <figure class="project__image">
                            <img src="images/project-03/sections-full.jpg" alt="Full building sections" loading="lazy">
                        </figure>
                    </div>
                </div>
            </div>
        </article>

        <!-- Project 04 -->
        <article class="project" data-project="04">
            <div class="project__hero">
                <img src="images/project-04/hero.jpg" alt="Historic building restoration — facade drawing showing restored ornamental details" loading="lazy">
            </div>
            <div class="project__info">
                <span class="project__number">04</span>
                <h2 class="project__title">Restoration, Redesign & Reuse</h2>
                <p class="project__location">Historic Buildings and Sites, Greece</p>
            </div>
            <p class="project__summary">
                Adaptive reuse of a historic building guided by principles of selective reversal of alterations, historical conservation, and modern adaptation. The building is repurposed as a functional resource centre for the academic community — with a library, design studios, and gathering spaces.
            </p>
            <button class="project__toggle" aria-expanded="false" aria-controls="project-04-details">
                More +
            </button>
            <div class="project__details" id="project-04-details" hidden>
                <div class="project__description">
                    <p>In restoring, adapting, and reactivating the historic building, the design approach prioritizes both the preservation of its historical and aesthetic value and its adaptation for contemporary use. The interventions are guided by a rigorous evaluation of the building's architectural integrity and its intended new functions.</p>
                    <p>Key principles: Selective Reversal of Alterations — removing modifications that detract from authenticity. Historical Conservation — retaining significant features to preserve identity. Targeted Restoration — partially restoring original typology, form, and materials. Balanced Interventions — bold changes where permissible, restraint where sensitive. Modern Adaptation — reconfiguring spaces for contemporary needs. Contrasts in Design — highlighting the interplay between historical preservation and modern requirements.</p>
                    <p>The building program: Ground floor is dedicated to a printing and laser area, materials storage, cafeteria, general storage, and restrooms. The first floor is designed as a library with reading and borrowing areas, a study area, a self-contained kitchen, and restrooms. The attic is envisioned as design studios for individual, group, and thesis work, with a rest area.</p>
                    <p>The proposed restoration and adaptive reuse address community needs for accessible gathering spaces and essential storage, while the attic studios respond to overcrowding issues in the Architecture Department.</p>
                </div>
                <div class="project__gallery">
                    <figure class="project__image project__image--full">
                        <img src="images/project-04/facade-restoration.jpg" alt="Detailed facade restoration drawing with pattern completion" loading="lazy">
                    </figure>
                    <div class="project__image-pair">
                        <figure class="project__image">
                            <img src="images/project-04/patterns.jpg" alt="Original witness patterns and ornamental details" loading="lazy">
                        </figure>
                        <figure class="project__image">
                            <img src="images/project-04/interiors.jpg" alt="Interior renders showing restored spaces" loading="lazy">
                        </figure>
                    </div>
                    <div class="project__image-pair">
                        <figure class="project__image">
                            <img src="images/project-04/floor-plans.jpg" alt="Floor plans showing new programme distribution" loading="lazy">
                        </figure>
                        <figure class="project__image">
                            <img src="images/project-04/use-diagrams.jpg" alt="Use diagrams colour-coded by function" loading="lazy">
                        </figure>
                    </div>
                </div>
            </div>
        </article>

    </main>

    <!-- About -->
    <section class="about">
        <h2 class="about__name">Eleni Chaziri</h2>
        <div class="about__bio">
            <p>I'm an architect with professional experience at Office25Architects, where I contributed to residential, commercial, and mixed-use developments. My work spans detailed architectural drawings, concept development, building permit submissions, and project coordination across multidisciplinary teams.</p>
            <p>I'm drawn to projects that prioritise sustainability, human connection, and cultural relevance — and I value the precision and care that complex architectural challenges demand.</p>
        </div>
        <div class="about__details">
            <div class="about__skills">
                <h3>Software</h3>
                <p>ArchiCAD, AutoCAD, Revit, Adobe Suite</p>
            </div>
            <div class="about__languages">
                <h3>Languages</h3>
                <p>English, Italian, Greek</p>
            </div>
        </div>
        <div class="about__contact">
            <a href="mailto:elenihaziri@gmail.com">elenihaziri@gmail.com</a>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <p>© Eleni Chaziri 2025</p>
    </footer>

    <script src="main.js"></script>
</body>
</html>
```

- [ ] **Step 2: Verify HTML renders in browser**

Run:
```bash
python -m http.server 8000
```
Open `http://localhost:8000` — verify the page renders with correct structure (content visible, no errors in console). Images will be broken until Task 1 is complete. Stop the server after verification.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add HTML structure with full content"
```

---

### Task 3: CSS Styling — Base & Typography

**Files:**
- Create: `styles.css`

- [ ] **Step 1: Create `styles.css` with reset, custom properties, and typography**

```css
/* ============================================
   Base & Custom Properties
   ============================================ */

*,
*::before,
*::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    /* Colours */
    --color-accent: #2C5F5C;
    --color-bg: #F8F7F5;
    --color-grey-light: #E8E6E3;
    --color-text: #3A3A3A;
    --color-heading: #1A1A1A;

    /* Typography */
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-size-body: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
    --font-size-small: 0.875rem;
    --font-size-project-number: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
    --font-size-project-title: clamp(1.25rem, 1.1rem + 0.75vw, 1.75rem);
    --font-size-h1: clamp(2rem, 1.5rem + 2.5vw, 3.5rem);
    --font-size-subtitle: clamp(0.875rem, 0.8rem + 0.375vw, 1.125rem);

    /* Spacing */
    --space-section: clamp(120px, 10vw, 160px);
    --space-project: clamp(100px, 8vw, 140px);
    --space-content: clamp(1rem, 1.5vw, 1.5rem);
    --content-width: min(900px, 90vw);
    --image-width: min(1200px, 95vw);

    /* Transitions */
    --transition-expand: 400ms ease;
}

html {
    font-size: 16px;
    scroll-behavior: smooth;
}

body {
    font-family: var(--font-family);
    font-size: var(--font-size-body);
    line-height: 1.6;
    color: var(--color-text);
    background-color: var(--color-bg);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

img {
    display: block;
    max-width: 100%;
    height: auto;
}

a {
    color: var(--color-accent);
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

h1, h2, h3 {
    color: var(--color-heading);
    font-weight: 500;
}
```

- [ ] **Step 2: Verify base styles apply**

Reload `http://localhost:8000` — background should be soft white, text graphite grey, sans-serif font active.

- [ ] **Step 3: Commit**

```bash
git add styles.css
git commit -m "feat: add base CSS with custom properties and typography"
```

---

### Task 4: CSS Styling — Header

**Files:**
- Modify: `styles.css`

- [ ] **Step 1: Add header styles to `styles.css`**

Append to `styles.css`:

```css
/* ============================================
   Header
   ============================================ */

.header {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    min-height: 100vh;
    padding: 2rem;
    position: relative;
}

.header__content {
    text-align: right;
    margin-right: 3rem;
}

.header__name {
    font-size: var(--font-size-h1);
    font-weight: 400;
    letter-spacing: 0.3em;
    color: var(--color-grey-light);
    text-transform: uppercase;
}

.header__title {
    font-size: var(--font-size-subtitle);
    letter-spacing: 0.2em;
    color: var(--color-grey-light);
    margin-top: 0.25rem;
}

.header__accent {
    position: absolute;
    right: 6%;
    top: 0;
    bottom: 0;
    width: 2px;
    background-color: var(--color-accent);
    opacity: 0.6;
}
```

- [ ] **Step 2: Verify header in browser**

Reload — header should fill viewport height, name right-aligned with generous letter-spacing in light grey, vertical accent line on the right side.

- [ ] **Step 3: Commit**

```bash
git add styles.css
git commit -m "feat: style header with accent line"
```

---

### Task 5: CSS Styling — Projects Section

**Files:**
- Modify: `styles.css`

- [ ] **Step 1: Add project styles to `styles.css`**

Append to `styles.css`:

```css
/* ============================================
   Projects
   ============================================ */

.projects {
    padding: 0 2rem;
}

.project {
    max-width: var(--image-width);
    margin: 0 auto;
    padding-top: var(--space-project);
}

.project:first-child {
    padding-top: var(--space-section);
}

.project__hero img {
    width: 100%;
    max-width: var(--image-width);
}

.project__info {
    max-width: var(--content-width);
    margin: var(--space-content) auto 0;
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    gap: 0.75rem;
}

.project__number {
    font-size: var(--font-size-project-number);
    font-weight: 400;
    letter-spacing: 0.1em;
    color: var(--color-accent);
    opacity: 0.7;
}

.project__title {
    font-size: var(--font-size-project-title);
    font-weight: 500;
    letter-spacing: 0.02em;
}

.project__location {
    width: 100%;
    font-size: var(--font-size-small);
    color: var(--color-text);
    opacity: 0.7;
    margin-top: -0.25rem;
}

.project__summary {
    max-width: var(--content-width);
    margin: var(--space-content) auto 0;
    line-height: 1.7;
}

.project__toggle {
    display: block;
    max-width: var(--content-width);
    margin: 1.5rem auto 0;
    background: none;
    border: none;
    font-family: var(--font-family);
    font-size: var(--font-size-small);
    color: var(--color-accent);
    cursor: pointer;
    letter-spacing: 0.05em;
    padding: 0.5rem 0;
    transition: opacity 200ms ease;
}

.project__toggle:hover {
    opacity: 0.7;
}

/* Expanded details */
.project__details {
    max-width: var(--image-width);
    margin: 0 auto;
    overflow: hidden;
    transition: max-height var(--transition-expand), opacity var(--transition-expand);
}

.project__details[hidden] {
    display: block;
    max-height: 0;
    opacity: 0;
    pointer-events: none;
}

.project__details:not([hidden]) {
    max-height: none;
    opacity: 1;
}

.project__description {
    max-width: var(--content-width);
    margin: 2rem auto;
}

.project__description p {
    margin-bottom: 1rem;
    line-height: 1.7;
}

.project__description p:last-child {
    margin-bottom: 0;
}

/* Gallery */
.project__gallery {
    margin-top: 2rem;
}

.project__gallery figure {
    margin-bottom: 1.5rem;
}

.project__image--full img {
    width: 100%;
}

.project__image-pair {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.project__image-pair img {
    width: 100%;
}
```

- [ ] **Step 2: Verify project layout in browser**

Reload — projects should stack vertically with generous spacing. Hero images should be large, text constrained to reading width, gallery images in full-width and paired grids.

- [ ] **Step 3: Commit**

```bash
git add styles.css
git commit -m "feat: style projects section with gallery grid"
```

---

### Task 6: CSS Styling — About & Footer

**Files:**
- Modify: `styles.css`

- [ ] **Step 1: Add about and footer styles to `styles.css`**

Append to `styles.css`:

```css
/* ============================================
   About
   ============================================ */

.about {
    max-width: var(--content-width);
    margin: 0 auto;
    padding: var(--space-section) 2rem;
    border-top: 1px solid var(--color-grey-light);
}

.about__name {
    font-size: var(--font-size-project-title);
    font-weight: 500;
    letter-spacing: 0.05em;
    margin-bottom: 1.5rem;
}

.about__bio p {
    margin-bottom: 1rem;
    line-height: 1.7;
}

.about__details {
    display: flex;
    gap: 3rem;
    margin-top: 2rem;
}

.about__details h3 {
    font-size: var(--font-size-small);
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
    color: var(--color-accent);
}

.about__details p {
    font-size: var(--font-size-body);
}

.about__contact {
    margin-top: 2rem;
}

.about__contact a {
    font-size: var(--font-size-body);
    letter-spacing: 0.02em;
}

/* ============================================
   Footer
   ============================================ */

.footer {
    max-width: var(--content-width);
    margin: 0 auto;
    padding: 2rem;
    text-align: left;
}

.footer p {
    font-size: var(--font-size-small);
    color: var(--color-text);
    opacity: 0.5;
}
```

- [ ] **Step 2: Verify about section and footer in browser**

Reload and scroll to bottom — About section should have a subtle top border, skills and languages side by side, footer text small and understated.

- [ ] **Step 3: Commit**

```bash
git add styles.css
git commit -m "feat: style about section and footer"
```

---

### Task 7: CSS Styling — Responsive Breakpoints

**Files:**
- Modify: `styles.css`

- [ ] **Step 1: Add responsive styles to `styles.css`**

Append to `styles.css`:

```css
/* ============================================
   Responsive
   ============================================ */

@media (max-width: 1199px) {
    .header__content {
        margin-right: 2rem;
    }

    .header__accent {
        right: 4%;
    }
}

@media (max-width: 767px) {
    .header {
        min-height: 80vh;
        padding: 1.5rem;
    }

    .header__content {
        margin-right: 1.5rem;
    }

    .header__accent {
        right: 3%;
    }

    .projects {
        padding: 0 1rem;
    }

    .project__image-pair {
        grid-template-columns: 1fr;
        gap: 1rem;
    }

    .about {
        padding: var(--space-section) 1rem;
    }

    .about__details {
        flex-direction: column;
        gap: 1.5rem;
    }

    .footer {
        padding: 2rem 1rem;
    }
}
```

- [ ] **Step 2: Test responsive behaviour**

Open browser DevTools, test at 375px (mobile), 768px (tablet), 1440px (desktop). Verify:
- Mobile: single column, image pairs stacked, header fills 80vh
- Tablet: slightly tighter spacing, images still paired
- Desktop: full layout with generous whitespace

- [ ] **Step 3: Commit**

```bash
git add styles.css
git commit -m "feat: add responsive breakpoints"
```

---

### Task 8: JavaScript — Expand/Collapse Interaction

**Files:**
- Create: `main.js`

- [ ] **Step 1: Create `main.js` with expand/collapse logic**

```javascript
/**
 * Portfolio — expand/collapse interaction for project details.
 */
(function () {
    'use strict';

    const toggleButtons = document.querySelectorAll('.project__toggle');

    toggleButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const targetId = button.getAttribute('aria-controls');
            const details = document.getElementById(targetId);
            const isExpanded = button.getAttribute('aria-expanded') === 'true';

            if (isExpanded) {
                // Collapse
                details.style.maxHeight = details.scrollHeight + 'px';
                // Force reflow
                details.offsetHeight;
                details.style.maxHeight = '0';
                details.style.opacity = '0';

                button.setAttribute('aria-expanded', 'false');
                button.textContent = 'More +';

                details.addEventListener('transitionend', function handler() {
                    details.hidden = true;
                    details.style.maxHeight = '';
                    details.style.opacity = '';
                    details.removeEventListener('transitionend', handler);
                }, { once: true });
            } else {
                // Expand
                details.hidden = false;
                details.style.maxHeight = '0';
                details.style.opacity = '0';
                // Force reflow
                details.offsetHeight;
                details.style.maxHeight = details.scrollHeight + 'px';
                details.style.opacity = '1';

                button.setAttribute('aria-expanded', 'true');
                button.textContent = 'Less −';

                details.addEventListener('transitionend', function handler() {
                    details.style.maxHeight = '';
                    details.removeEventListener('transitionend', handler);
                }, { once: true });
            }
        });
    });
})();
```

- [ ] **Step 2: Test expand/collapse in browser**

Reload page, click "More +" on any project. Verify:
- Details section smoothly expands (height and opacity transition)
- Button text changes to "Less −"
- Clicking "Less −" smoothly collapses back
- Multiple projects can be expanded independently
- No console errors

- [ ] **Step 3: Commit**

```bash
git add main.js
git commit -m "feat: add expand/collapse interaction with smooth transitions"
```

---

### Task 9: Load Web Font

**Files:**
- Modify: `index.html`

- [ ] **Step 1: Add Inter font from Google Fonts**

Add the following inside `<head>` in `index.html`, before the `styles.css` link:

```html
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
```

- [ ] **Step 2: Verify font loads**

Reload page — text should render in Inter. Check Network tab to confirm font files load.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: load Inter font from Google Fonts"
```

---

### Task 10: Final Polish & Verification

**Files:**
- Modify: `styles.css` (minor adjustments if needed)
- Modify: `index.html` (add favicon placeholder)

- [ ] **Step 1: Add a minimal favicon to prevent 404**

Add inside `<head>` in `index.html`:

```html
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect fill='%232C5F5C' width='100' height='100' rx='12'/></svg>">
```

- [ ] **Step 2: Full page walkthrough**

Open `http://localhost:8000` and verify the complete experience:
- Header renders with accent line and spaced typography
- All four projects visible in vertical stack
- Hero images display (or show broken image icons if images not yet extracted — this is acceptable)
- Expand/collapse works on all four projects
- About section displays with bio, skills, languages, email link
- Footer shows copyright
- Responsive: test at 375px, 768px, 1440px
- Email link opens mail client
- No console errors

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add inline SVG favicon"
```

- [ ] **Step 4: Add .gitignore entry for scripts**

Append to `.gitignore`:

```
scripts/
```

- [ ] **Step 5: Final commit**

```bash
git add .gitignore
git commit -m "chore: ignore scripts directory"
```

---

## Task Dependency Note

Task 1 (image extraction) is independent of Tasks 2–10. The HTML/CSS/JS can be built
and verified structurally without images — broken image icons will appear where images
are missing, but layout and interactions are testable. Task 1 can run in parallel or
after the code tasks.

The recommended execution order is: **2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10**, with
Task 1 done before or after (images are needed for final verification but not for
building the code).
