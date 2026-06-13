#!/usr/bin/env python3
"""Extract images from portfolio PDF into project folders.

Uses PyMuPDF to extract embedded images at their native resolution.
Filters out very small images (icons, UI elements) and saves the rest
organized by project.

Usage:
    cd scripts/
    uv run extract_images.py
"""

import fitz  # PyMuPDF
from pathlib import Path

# Paths relative to project root (script runs from scripts/)
PROJECT_ROOT = Path(__file__).parent.parent
PDF_PATH = PROJECT_ROOT / "assets" / "portfolio.pdf"
OUTPUT_DIR = PROJECT_ROOT / "images"

# Page ranges per project (0-indexed for PyMuPDF)
# Page 0: cover
# Page 1: table of contents
# Pages 2-3: Project 01 (Xanthi City Pavilion)
# Pages 4-9: Project 02 (Tobacco Warehouse)
# Pages 10-11: Project 03 (Samothrace Spa)
# Pages 12-13: Project 04 (Historic Restoration)
PROJECT_PAGES = {
    "project-01": [2, 3],
    "project-02": [4, 5, 6, 7, 8, 9],
    "project-03": [10, 11],
    "project-04": [12, 13],
}

# Minimum image size in bytes to keep (filters out tiny UI elements)
MIN_IMAGE_SIZE = 10_000

# Minimum pixel dimensions to keep
MIN_DIMENSION = 100


def extract_images():
    """Extract all meaningful images from the portfolio PDF."""
    doc = fitz.open(str(PDF_PATH))
    print(f"Opened: {PDF_PATH} ({doc.page_count} pages)")

    for project, pages in PROJECT_PAGES.items():
        project_dir = OUTPUT_DIR / project
        project_dir.mkdir(parents=True, exist_ok=True)

        img_count = 0
        seen_xrefs = set()  # Avoid duplicate images across pages

        for page_num in pages:
            page = doc[page_num]
            images = page.get_images(full=True)

            for img_info in images:
                xref = img_info[0]

                # Skip duplicates (same image referenced on multiple pages)
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                width = base_image["width"]
                height = base_image["height"]
                ext = base_image["ext"]

                # Filter out small images
                if len(image_bytes) < MIN_IMAGE_SIZE:
                    continue
                if width < MIN_DIMENSION or height < MIN_DIMENSION:
                    continue

                img_count += 1
                filename = f"image-{img_count:02d}.{ext}"
                filepath = project_dir / filename

                with open(filepath, "wb") as f:
                    f.write(image_bytes)

                print(f"  {project}/{filename}  ({width}x{height}, {len(image_bytes) // 1024}KB)")

        print(f"  → {project}: {img_count} images extracted")

    doc.close()
    print("\nDone.")
    print("\nNext step: review images/ and rename the first/best render")
    print("in each project folder to 'hero.jpg'. Rename others to match")
    print("the filenames referenced in index.html:")
    print("  project-01: hero, interior, section, diagrams, plans, elevations")
    print("  project-02: hero, site-plan, facade-east, facade-south,")
    print("              damage-mapping, materials, sections,")
    print("              restoration-plans, restoration-sections,")
    print("              proposal-description, interiors")
    print("  project-03: hero, render-landscape, section-site,")
    print("              renders-views, sections-full")
    print("  project-04: hero, facade-restoration, patterns, interiors,")
    print("              floor-plans, use-diagrams")


if __name__ == "__main__":
    extract_images()
