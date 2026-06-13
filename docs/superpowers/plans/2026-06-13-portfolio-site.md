# Portfolio Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the static portfolio website specified in `docs/superpowers/specs/2026-06-13-portfolio-site-design.md` — index, about, and four project pages, served by GitHub Pages from this repo.

**Architecture:** Pure static HTML and CSS. No JavaScript frameworks; no runtime build step. The only "build" is a Python image-optimization script in `scripts/` that produces responsive JPEG variants under `images/web/` (committed to git). All paths are relative so the site loads correctly from a GitHub Pages project subpath. Three CSS files split by responsibility: `base.css` (tokens, reset, typography, layout primitives), `site.css` (header/nav/index/about), `project.css` (spread primitives, project headers, captions). Per-page differences live in HTML class composition, not in extra stylesheets.

**Tech Stack:** HTML5, CSS3 (custom properties, Grid, `clamp()`), self-hosted Jost font (SIL OFL 1.1), Python 3.13 + Pillow + pytest for the image pipeline (uv-managed).

---

## File plan

**Created:**

```
docs/superpowers/plans/2026-06-13-portfolio-site.md   ← this plan

scripts/optimize_images.py                            ← responsive JPEG variants + manifest
scripts/test_optimize_images.py                       ← pytest tests for the script

styles/base.css                                       ← reset, tokens, type scale, layout primitives
styles/site.css                                       ← header/nav, index page, about page
styles/project.css                                    ← spread primitives, project header, captions
styles/fonts/jost-300.woff2                           ← downloaded
styles/fonts/jost-400.woff2                           ← downloaded
styles/fonts/jost-700.woff2                           ← downloaded
styles/fonts/OFL.txt                                  ← SIL Open Font License 1.1

index.html                                            ← landing
about.html                                            ← profile, CV content, contact (#contact)
projects/01-xanthi-pavilion.html
projects/02-tobacco-warehouse.html
projects/03-therma-spa.html
projects/04-historic-restoration.html

images/web/project-01/<name>-{1600,800,400}.jpg       ← generated, committed
images/web/project-02/<name>-{1600,800,400}.jpg       ← generated (image-07 excluded), committed
images/web/project-03/<name>-{1600,800,400}.jpg       ← generated, committed
images/web/project-04/<name>-{1600,800,400}.jpg       ← generated, committed
images/web/_manifest.json                             ← intrinsic dimensions of each source
```

**Modified:**

```
scripts/pyproject.toml                                ← add pillow + pytest dependencies
CLAUDE.md                                             ← replace "single-page" line; document path conventions
```

**Untouched:**

`assets/`, `docs/vision.md`, `images/project-XX/` originals.

---

## TDD note for HTML/CSS work

A static HTML/CSS portfolio has no unit-test framework that fits the work. We TDD the Python image script (where TDD genuinely helps) and use **explicit verification steps** for HTML/CSS tasks:

- Run `tidy -q -e` (HTML5 validator) on every HTML file to catch markup errors.
- Open the page in a real browser at three viewport widths (360px, 768px, 1440px) and visually compare against the spec.
- Run Lighthouse (Chrome DevTools) on the final pages — accessibility score must be 100, no contrast warnings.
- Check `cls` (Cumulative Layout Shift) is ≈ 0 on each page.

Each HTML/CSS task lists the exact verification commands and expected results.


---

## Section 1 — Image pipeline (Tasks 1–5)

Delivers a working `scripts/optimize_images.py` and a populated `images/web/` tree plus `images/web/_manifest.json`. The pipeline is TDD'd because the rest of the build depends on its outputs.

---

### Task 1: Add Pillow and pytest to scripts environment

**Files:**
- Modify: `scripts/pyproject.toml`

- [ ] **Step 1: Replace the dependencies block**

Replace the entire contents of `scripts/pyproject.toml` with:

```toml
[project]
name = "extract-images"
version = "0.1.0"
description = "Extract and optimize project images for the portfolio site"
requires-python = ">=3.13"
dependencies = [
    "pymupdf>=1.27.2.3",
    "pillow>=11.0.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0.0",
]
```

- [ ] **Step 2: Sync the environment**

Run: `cd scripts && uv sync`

Expected: completes without error; `pillow` and `pytest` appear in `scripts/uv.lock`.

- [ ] **Step 3: Verify Pillow imports**

Run: `cd scripts && uv run python -c "from PIL import Image; print(Image.__version__)"`

Expected: prints a version starting with `11.` (or whatever uv resolved within the constraint).

- [ ] **Step 4: Verify pytest is callable**

Run: `cd scripts && uv run python -m pytest --version`

Expected: prints a version starting with `pytest 8.`.

- [ ] **Step 5: Commit**

```bash
git add scripts/pyproject.toml scripts/uv.lock
git commit -m "Add pillow and pytest to scripts environment"
```

---

### Task 2: Failing test for `iter_sources`

**Files:**
- Create: `scripts/test_optimize_images.py`

`iter_sources(images_root)` walks `images/project-XX/` and yields every source image path, **excluding** `project-02/image-07.jpeg`. Yields nothing from `images/web/`.

- [ ] **Step 1: Write the failing test**

Create `scripts/test_optimize_images.py` with this content:

```python
"""Tests for optimize_images.py.

Run from scripts/:
    uv run python -m pytest test_optimize_images.py -v
"""

from pathlib import Path

from optimize_images import iter_sources, EXCLUDED


def make_tree(root: Path) -> None:
    """Build a fake images/ tree the tests can scan."""
    (root / "project-01").mkdir(parents=True)
    (root / "project-02").mkdir(parents=True)
    (root / "project-03").mkdir(parents=True)
    (root / "web").mkdir(parents=True)  # generated; must be skipped

    (root / "project-01" / "image-01.jpeg").write_bytes(b"x")
    (root / "project-01" / "image-02.jpeg").write_bytes(b"x")
    (root / "project-02" / "image-06.jpeg").write_bytes(b"x")
    (root / "project-02" / "image-07.jpeg").write_bytes(b"x")  # excluded
    (root / "project-02" / "image-08.png").write_bytes(b"x")
    (root / "project-03" / "image-01.jpeg").write_bytes(b"x")
    (root / "web" / "leftover.jpeg").write_bytes(b"x")  # must be ignored


def test_iter_sources_yields_all_project_images_except_excluded(tmp_path):
    make_tree(tmp_path)

    found = sorted((p.parent.name, p.name) for p in iter_sources(tmp_path))

    assert found == [
        ("project-01", "image-01.jpeg"),
        ("project-01", "image-02.jpeg"),
        ("project-02", "image-06.jpeg"),
        ("project-02", "image-08.png"),
        ("project-03", "image-01.jpeg"),
    ]


def test_iter_sources_excludes_project_02_image_07(tmp_path):
    make_tree(tmp_path)
    paths = {(p.parent.name, p.name) for p in iter_sources(tmp_path)}
    assert ("project-02", "image-07.jpeg") not in paths


def test_excluded_constant_contains_project_02_image_07():
    assert ("project-02", "image-07.jpeg") in EXCLUDED


def test_iter_sources_skips_web_directory(tmp_path):
    make_tree(tmp_path)
    yielded = list(iter_sources(tmp_path))
    assert all(p.parent.name != "web" for p in yielded)
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd scripts && uv run python -m pytest test_optimize_images.py -v`

Expected: collection FAILS with `ModuleNotFoundError: No module named 'optimize_images'`.

- [ ] **Step 3: Commit the failing test**

```bash
git add scripts/test_optimize_images.py
git commit -m "Add failing tests for optimize_images.iter_sources"
```

---

### Task 3: Implement `iter_sources`

**Files:**
- Create: `scripts/optimize_images.py`

- [ ] **Step 1: Write the minimal implementation**

Create `scripts/optimize_images.py` with this content:

```python
#!/usr/bin/env python3
"""Generate web-optimized image variants from images/project-XX/ originals.

Outputs three JPEG variants per source (1600w, 800w, 400w) into
images/web/project-XX/<name>-{1600,800,400}.jpg, plus a manifest of
intrinsic source dimensions for HTML authoring.

Idempotent: skips outputs newer than their source.

Usage:
    cd scripts/
    uv run optimize_images.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_ROOT = PROJECT_ROOT / "images"

# Per the vision doc: project-2/image-07.jpeg should not be used on the site.
EXCLUDED: set[tuple[str, str]] = {
    ("project-02", "image-07.jpeg"),
}

PROJECT_DIR_PREFIX = "project-"
ALLOWED_SUFFIXES = {".jpeg", ".jpg", ".png"}


def iter_sources(images_root: Path) -> Iterable[Path]:
    """Yield every source image under images/project-XX/, sorted, excluding EXCLUDED."""
    for project_dir in sorted(images_root.iterdir()):
        if not project_dir.is_dir():
            continue
        if not project_dir.name.startswith(PROJECT_DIR_PREFIX):
            continue
        for src in sorted(project_dir.iterdir()):
            if src.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            if (project_dir.name, src.name) in EXCLUDED:
                continue
            yield src


if __name__ == "__main__":
    for src in iter_sources(IMAGES_ROOT):
        print(src.relative_to(PROJECT_ROOT))
```

- [ ] **Step 2: Run the tests to verify they pass**

Run: `cd scripts && uv run python -m pytest test_optimize_images.py -v`

Expected: 4 passed.

- [ ] **Step 3: Smoke-run against real images**

Run: `cd scripts && uv run optimize_images.py`

Expected: prints a list of source paths. Confirm by eye:
- `images/project-01/image-01.jpeg` is in the output.
- `images/project-02/image-07.jpeg` is **not** in the output.
- Total source count is 60 (11 + 27 + 10 + 12).

- [ ] **Step 4: Commit**

```bash
git add scripts/optimize_images.py
git commit -m "Implement iter_sources for image optimization pipeline"
```

---

### Task 4: Add `build_variants` and `write_manifest` (TDD)

**Files:**
- Modify: `scripts/test_optimize_images.py`
- Modify: `scripts/optimize_images.py`

`build_variants(src, out_dir, stem)` produces the three JPEG variants. `write_manifest(images_root, web_root)` writes `_manifest.json` listing the intrinsic dimensions of each source (used during HTML authoring to set `width`/`height` attributes and prevent layout shift).

- [ ] **Step 1: Append failing tests**

Append the following to `scripts/test_optimize_images.py`:

```python
import json

from PIL import Image

from optimize_images import build_variants, write_manifest, VARIANT_WIDTHS


def make_real_jpeg(path: Path, width: int, height: int) -> None:
    """Write a real JPEG of the given size so PIL can open it."""
    Image.new("RGB", (width, height), (200, 200, 200)).save(path, "JPEG", quality=85)


def test_variant_widths_constant():
    assert VARIANT_WIDTHS == (1600, 800, 400)


def test_build_variants_produces_three_widths(tmp_path):
    src = tmp_path / "src.jpeg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    make_real_jpeg(src, 3200, 2400)

    written = build_variants(src, out_dir, "src")

    assert {p.name for p in written} == {"src-1600.jpg", "src-800.jpg", "src-400.jpg"}
    for path in written:
        with Image.open(path) as img:
            target = int(path.stem.split("-")[-1])
            assert img.width == target
            assert img.format == "JPEG"


def test_build_variants_does_not_upscale(tmp_path):
    src = tmp_path / "small.jpeg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    make_real_jpeg(src, 600, 400)  # smaller than the 800 and 1600 variants

    written = build_variants(src, out_dir, "small")

    sizes = {}
    for path in written:
        with Image.open(path) as img:
            sizes[path.name] = img.width
    # 1600 and 800 variants are clamped to source width, never upscaled.
    assert sizes == {"small-1600.jpg": 600, "small-800.jpg": 600, "small-400.jpg": 400}


def test_build_variants_is_idempotent(tmp_path):
    src = tmp_path / "src.jpeg"
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    make_real_jpeg(src, 3200, 2400)

    first = build_variants(src, out_dir, "src")
    mtimes_first = {p: p.stat().st_mtime_ns for p in first}

    second = build_variants(src, out_dir, "src")
    mtimes_second = {p: p.stat().st_mtime_ns for p in second}

    # Same files reported, and no rewrite happened (mtime unchanged).
    assert {p.name for p in first} == {p.name for p in second}
    assert mtimes_first == mtimes_second


def test_write_manifest_records_intrinsic_dimensions(tmp_path):
    project_dir = tmp_path / "project-01"
    project_dir.mkdir()
    make_real_jpeg(project_dir / "image-01.jpeg", 1200, 800)
    make_real_jpeg(project_dir / "image-02.jpeg", 600, 900)

    web_root = tmp_path / "web"
    web_root.mkdir()

    write_manifest(tmp_path, web_root)

    data = json.loads((web_root / "_manifest.json").read_text())

    assert data["project-01/image-01"] == {"width": 1200, "height": 800}
    assert data["project-01/image-02"] == {"width": 600, "height": 900}


def test_write_manifest_excludes_project_02_image_07(tmp_path):
    project_dir = tmp_path / "project-02"
    project_dir.mkdir()
    make_real_jpeg(project_dir / "image-06.jpeg", 100, 100)
    make_real_jpeg(project_dir / "image-07.jpeg", 100, 100)  # excluded

    web_root = tmp_path / "web"
    web_root.mkdir()

    write_manifest(tmp_path, web_root)
    data = json.loads((web_root / "_manifest.json").read_text())

    assert "project-02/image-06" in data
    assert "project-02/image-07" not in data
```

- [ ] **Step 2: Run the tests to verify the new ones fail**

Run: `cd scripts && uv run python -m pytest test_optimize_images.py -v`

Expected: 4 original tests pass; 6 new tests FAIL with `ImportError: cannot import name 'build_variants'` (or equivalent for `write_manifest` / `VARIANT_WIDTHS`).

- [ ] **Step 3: Replace `scripts/optimize_images.py` with the full implementation**

Replace the entire contents of `scripts/optimize_images.py` with:

```python
#!/usr/bin/env python3
"""Generate web-optimized image variants from images/project-XX/ originals.

Outputs three JPEG variants per source (1600w, 800w, 400w) into
images/web/project-XX/<name>-{1600,800,400}.jpg, plus a manifest of
intrinsic source dimensions for HTML authoring.

Idempotent: skips outputs newer than their source.

Usage:
    cd scripts/
    uv run optimize_images.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageOps

PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_ROOT = PROJECT_ROOT / "images"
WEB_ROOT = IMAGES_ROOT / "web"

# Per the vision doc: project-2/image-07.jpeg should not be used on the site.
EXCLUDED: set[tuple[str, str]] = {
    ("project-02", "image-07.jpeg"),
}

PROJECT_DIR_PREFIX = "project-"
ALLOWED_SUFFIXES = {".jpeg", ".jpg", ".png"}

# Variant widths in px.
VARIANT_WIDTHS: tuple[int, int, int] = (1600, 800, 400)
JPEG_QUALITY = 82


def iter_sources(images_root: Path) -> Iterable[Path]:
    """Yield every source image under images/project-XX/, sorted, excluding EXCLUDED."""
    for project_dir in sorted(images_root.iterdir()):
        if not project_dir.is_dir():
            continue
        if not project_dir.name.startswith(PROJECT_DIR_PREFIX):
            continue
        for src in sorted(project_dir.iterdir()):
            if src.suffix.lower() not in ALLOWED_SUFFIXES:
                continue
            if (project_dir.name, src.name) in EXCLUDED:
                continue
            yield src


def _is_fresh(src: Path, dst: Path) -> bool:
    """True if dst exists and is at least as new as src."""
    return dst.exists() and dst.stat().st_mtime_ns >= src.stat().st_mtime_ns


def build_variants(src: Path, out_dir: Path, stem: str) -> list[Path]:
    """Produce 1600/800/400 JPEG variants of src in out_dir.

    Returns the list of output paths (always all three, even when widths are
    clamped to the source width — we never upscale). Skips writes when the
    output is already up to date.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    with Image.open(src) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        source_width = img.width

        for target in VARIANT_WIDTHS:
            dst = out_dir / f"{stem}-{target}.jpg"
            written.append(dst)
            if _is_fresh(src, dst):
                continue

            width = min(target, source_width)
            if width == img.width:
                resized = img.copy()
            else:
                ratio = width / img.width
                height = max(1, round(img.height * ratio))
                resized = img.resize((width, height), Image.LANCZOS)

            resized.save(
                dst,
                format="JPEG",
                quality=JPEG_QUALITY,
                progressive=True,
                optimize=True,
            )

    return written


def write_manifest(images_root: Path, web_root: Path) -> None:
    """Write web_root/_manifest.json mapping 'project-XX/<stem>' -> {width, height}.

    The manifest records intrinsic source dimensions; HTML authors use it to
    set width/height attributes on <img> tags so the page does not shift as
    images load.
    """
    web_root.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict[str, int]] = {}

    for src in iter_sources(images_root):
        with Image.open(src) as img:
            img = ImageOps.exif_transpose(img)
            key = f"{src.parent.name}/{src.stem}"
            manifest[key] = {"width": img.width, "height": img.height}

    (web_root / "_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )


def main() -> None:
    print(f"Images root: {IMAGES_ROOT}")
    print(f"Web output:  {WEB_ROOT}")

    count = 0
    for src in iter_sources(IMAGES_ROOT):
        out_dir = WEB_ROOT / src.parent.name
        written = build_variants(src, out_dir, src.stem)
        count += 1
        print(f"  {src.parent.name}/{src.name} -> {len(written)} variants")

    write_manifest(IMAGES_ROOT, WEB_ROOT)
    print(f"\n{count} sources processed; manifest written to {WEB_ROOT}/_manifest.json")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd scripts && uv run python -m pytest test_optimize_images.py -v`

Expected: 10 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/optimize_images.py scripts/test_optimize_images.py
git commit -m "Add build_variants and write_manifest with idempotent caching"
```

---

### Task 5: Run the pipeline against real images and commit outputs

**Files:**
- Create: `images/web/project-01/...` (generated)
- Create: `images/web/project-02/...` (generated, image-07 excluded)
- Create: `images/web/project-03/...` (generated)
- Create: `images/web/project-04/...` (generated)
- Create: `images/web/_manifest.json` (generated)

- [ ] **Step 1: Run the optimizer**

Run: `cd scripts && uv run optimize_images.py`

Expected: prints one line per source ending with `-> 3 variants`. Final line reports `60 sources processed; manifest written to .../images/web/_manifest.json`.

- [ ] **Step 2: Verify the output tree**

Run: `find images/web -type f | sort | head -30`

Expected: paths like `images/web/_manifest.json`, `images/web/project-01/image-01-1600.jpg`, `images/web/project-01/image-01-800.jpg`, `images/web/project-01/image-01-400.jpg`, etc.

- [ ] **Step 3: Verify exclusion**

Run: `ls images/web/project-02/ | grep image-07 || echo "OK - excluded"`

Expected: prints `OK - excluded`.

- [ ] **Step 4: Verify variant counts**

Run: `find images/web -name '*.jpg' | wc -l`

Expected: `180` (60 sources × 3 variants).

- [ ] **Step 5: Verify idempotence**

Run: `cd scripts && uv run optimize_images.py` again, then `find images/web -name '*.jpg' -newer images/web/project-01/image-01-1600.jpg | wc -l`

Expected: the second run completes quickly (no rewrites) and the count is `0`.

- [ ] **Step 6: Spot-check a manifest entry**

Run: `python3 -c "import json; m = json.load(open('images/web/_manifest.json')); print(m['project-01/image-01'])"`

Expected: prints something like `{'width': 1535, 'height': 850}` (numbers will vary; the shape is the assertion).

- [ ] **Step 7: Commit the generated outputs**

```bash
git add images/web/
git commit -m "Generate web-optimized image variants and manifest"
```

---


## Section 2 — Foundations (Tasks 6–9)

Sets up the font files and the three CSS files that every page builds on.

After this section the site has no pages yet, but every page that follows will compose primitives defined here. No regressions possible: changes happen behind class names that pages will use later.

---

### Task 6: Self-host the Jost font and its license

**Files:**
- Create: `styles/fonts/jost-300.woff2`
- Create: `styles/fonts/jost-400.woff2`
- Create: `styles/fonts/jost-700.woff2`
- Create: `styles/fonts/OFL.txt`

Jost is the freely-licensed stand-in for Century Gothic specified in §3 of the design spec. We self-host the .woff2 files; **no Google Fonts request at runtime**.

- [ ] **Step 1: Make the fonts directory**

Run: `mkdir -p styles/fonts`

- [ ] **Step 2: Download the three weights from the official source**

Run each command in turn:

```bash
curl -fsSL -o styles/fonts/jost-300.woff2 \
  https://fonts.gstatic.com/s/jost/v15/92zPtBhPNqw79Ij1E865zBUv7myrJ-VdcA.woff2

curl -fsSL -o styles/fonts/jost-400.woff2 \
  https://fonts.gstatic.com/s/jost/v15/92zPtBhPNqw79Ij1E865zBUv7mKrJ-VdcA.woff2

curl -fsSL -o styles/fonts/jost-700.woff2 \
  https://fonts.gstatic.com/s/jost/v15/92zPtBhPNqw79Ij1E865zBUv7nyrJ-VdcA.woff2
```

If any URL 404s (Google rotates these occasionally), fall back to fonts.google.com:
1. Visit https://fonts.google.com/specimen/Jost
2. Click "Get font" → "Download all".
3. From the downloaded ZIP, extract the static `Jost-Light.ttf`, `Jost-Regular.ttf`, `Jost-Bold.ttf`.
4. Convert each TTF to WOFF2 using `woff2_compress` (Debian/Ubuntu: `apt install woff2`):
   ```bash
   woff2_compress Jost-Light.ttf   && mv Jost-Light.woff2   styles/fonts/jost-300.woff2
   woff2_compress Jost-Regular.ttf && mv Jost-Regular.woff2 styles/fonts/jost-400.woff2
   woff2_compress Jost-Bold.ttf    && mv Jost-Bold.woff2    styles/fonts/jost-700.woff2
   ```

Expected: three files exist; each is between 20 KB and 60 KB.

- [ ] **Step 3: Verify file sizes are sensible**

Run: `ls -l styles/fonts/*.woff2`

Expected: three lines, each file ≥ 20000 bytes and ≤ 80000 bytes. (A 0-byte file means the curl failed silently — re-run.)

- [ ] **Step 4: Add the SIL Open Font License**

Create `styles/fonts/OFL.txt` with the text from https://openfontlicense.org/ — the canonical text starts:

```
Copyright 2018 The Jost Project Authors (https://github.com/indestructible-type/Jost)

This Font Software is licensed under the SIL Open Font License, Version 1.1.
This license is copied below, and is also available with a FAQ at:
https://openfontlicense.org

-----------------------------------------------------------
SIL OPEN FONT LICENSE Version 1.1 - 26 February 2007
-----------------------------------------------------------

PREAMBLE
The goals of the Open Font License (OFL) are to stimulate worldwide
development of collaborative font projects, to support the font creation
efforts of academic and linguistic communities, and to provide a free and
open framework in which fonts may be shared and improved in partnership
with others.

The OFL allows the licensed fonts to be used, studied, modified and
redistributed freely as long as they are not sold by themselves. The
fonts, including any derivative works, can be bundled, embedded,
redistributed and/or sold with any software provided that any reserved
names are not used by derivative works. The fonts and derivatives,
however, cannot be released under any other type of license. The
requirement for fonts to remain under this license does not apply to any
document created using the fonts or their derivatives.

DEFINITIONS
"Font Software" refers to the set of files released by the Copyright
Holder(s) under this license and clearly marked as such. This may
include source files, build scripts and documentation.

"Reserved Font Name" refers to any names specified as such after the
copyright statement(s).

"Original Version" refers to the collection of Font Software components
as distributed by the Copyright Holder(s).

"Modified Version" refers to any derivative made by adding to, deleting,
or substituting -- in part or in whole -- any of the components of the
Original Version, by changing formats or by porting the Font Software to
a new environment.

"Author" refers to any designer, engineer, programmer, technical writer
or other person who contributed to the Font Software.

PERMISSION & CONDITIONS
Permission is hereby granted, free of charge, to any person obtaining a
copy of the Font Software, to use, study, copy, merge, embed, modify,
redistribute, and sell modified and unmodified copies of the Font
Software, subject to the following conditions:

1) Neither the Font Software nor any of its individual components, in
Original or Modified Versions, may be sold by itself.

2) Original or Modified Versions of the Font Software may be bundled,
redistributed and/or sold with any software, provided that each copy
contains the above copyright notice and this license. These can be
included either as stand-alone text files, human-readable headers or
in the appropriate machine-readable metadata fields within text or
binary files as long as those fields can be easily viewed by the user.

3) No Modified Version of the Font Software may use the Reserved Font
Name(s) unless explicit written permission is granted by the corresponding
Copyright Holder. This restriction only applies to the primary font name
as presented to the users.

4) The name(s) of the Copyright Holder(s) or the Author(s) of the Font
Software shall not be used to promote, endorse or advertise any
Modified Version, except to acknowledge the contribution(s) of the
Copyright Holder(s) and the Author(s) or with their explicit written
permission.

5) The Font Software, modified or unmodified, in part or in whole,
must be distributed entirely under this license, and must not be
distributed under any other license. The requirement for fonts to
remain under this license does not apply to any document created
using the Font Software.

TERMINATION
This license becomes null and void if any of the above conditions are
not met.

DISCLAIMER
THE FONT SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO ANY WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
OF COPYRIGHT, PATENT, TRADEMARK, OR OTHER RIGHT. IN NO EVENT SHALL THE
COPYRIGHT HOLDER BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
INCLUDING ANY GENERAL, SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL
DAMAGES, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF THE USE OR INABILITY TO USE THE FONT SOFTWARE OR FROM
OTHER DEALINGS IN THE FONT SOFTWARE.
```

- [ ] **Step 5: Commit**

```bash
git add styles/fonts/
git commit -m "Self-host Jost font (300/400/700) under OFL"
```

---

### Task 7: Create `styles/base.css` — tokens, reset, typography, layout primitives

**Files:**
- Create: `styles/base.css`

This is the foundation every other stylesheet depends on. Defines colour and spacing tokens, a minimal reset, the type scale, the `.frame` page wrapper, and the `.spread*` layout primitives.

- [ ] **Step 1: Create the file**

Create `styles/base.css` with this content:

```css
/* ============================================================
   base.css — design tokens, reset, typography, layout primitives.
   Loaded first on every page. Has no page-specific selectors.
   ============================================================ */

/* ---------- Fonts ----------------------------------------- */

@font-face {
  font-family: 'Jost';
  font-style: normal;
  font-weight: 300;
  font-display: swap;
  src: url('fonts/jost-300.woff2') format('woff2');
}
@font-face {
  font-family: 'Jost';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('fonts/jost-400.woff2') format('woff2');
}
@font-face {
  font-family: 'Jost';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('fonts/jost-700.woff2') format('woff2');
}

/* ---------- Tokens ---------------------------------------- */

:root {
  --ink:    #1A1A1A;
  --body:   #3A3A3A;
  --accent: #2C5F5C;
  --bg:     #FFFFFF;
  --mute:   #E8E6E3;
  --rule:   #D6D4D1;

  --font-sans: 'Jost', 'Century Gothic', 'CenturyGothic', 'URW Gothic', sans-serif;

  /* 8px rhythm. Use multiples; do not introduce ad-hoc spacings. */
  --s-1: 0.5rem;   /*  8px */
  --s-2: 1rem;     /* 16px */
  --s-3: 1.5rem;   /* 24px */
  --s-4: 2rem;     /* 32px */
  --s-5: 3rem;     /* 48px */
  --s-6: 4.5rem;   /* 72px */
  --s-7: 6rem;     /* 96px */

  /* Side gutter: fluid, capped. */
  --gutter: clamp(1.5rem, 5vw, 6rem);

  /* Section vertical rhythm. */
  --section-y: clamp(3rem, 8vw, 6rem);

  --rule-thin: 1px;
}

/* ---------- Minimal reset --------------------------------- */

*, *::before, *::after { box-sizing: border-box; }

html, body { margin: 0; padding: 0; }

body {
  font-family: var(--font-sans);
  font-weight: 400;
  font-size: 1rem;
  line-height: 1.65;
  color: var(--body);
  background: var(--bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

img, svg { display: block; max-width: 100%; height: auto; }

a {
  color: var(--accent);
  text-decoration: none;
}
a:hover { opacity: 0.7; transition: opacity 200ms ease; }

a:focus-visible,
button:focus-visible {
  outline: var(--rule-thin) solid var(--accent);
  outline-offset: 2px;
}

ul { list-style: none; padding: 0; margin: 0; }

h1, h2, h3, h4 {
  margin: 0;
  color: var(--ink);
  font-weight: 700;
  line-height: 1.2;
}

p { margin: 0 0 var(--s-2); max-width: 62ch; }

/* ---------- Typography scale ------------------------------ */

.t-hero {
  font-weight: 700;
  font-size: clamp(2rem, 5vw, 3.5rem);
  letter-spacing: 0.4em;
  text-transform: uppercase;
  line-height: 1.1;
  color: var(--ink);
}

.t-hero-sub {
  font-weight: 400;
  font-size: clamp(0.9rem, 1.4vw, 1.125rem);
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--accent);
}

.t-hero-meta {
  font-weight: 300;
  font-size: 0.8125rem;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--body);
}

.t-h1 {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 700;
  color: var(--ink);
}

.t-h2 {
  font-size: 1.25rem;
  font-weight: 400;
  color: var(--ink);
}

.t-caption {
  font-size: 0.8125rem;
  font-weight: 300;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--body);
  line-height: 1.4;
}

.t-numeral {
  font-weight: 300;
  font-size: clamp(2rem, 5vw, 3.5rem);
  color: var(--accent);
  line-height: 1;
  letter-spacing: 0.05em;
}

/* ---------- Layout primitives ----------------------------- */

.frame {
  max-width: 1440px;
  margin: 0 auto;
  padding-left: var(--gutter);
  padding-right: var(--gutter);
}

.rule {
  border: 0;
  border-top: var(--rule-thin) solid var(--rule);
  margin: var(--s-5) 0;
}

.rule--accent {
  border-top-color: var(--accent);
}

/* Spread primitives: vertical blocks composed by HTML. */

.spread {
  margin-block: var(--section-y);
}

.spread--text-only {
  max-width: 62ch;
  margin-inline: auto;
}

.spread--full > img,
.spread--full > picture > img {
  width: 100%;
}

.spread--two-up,
.spread--three-up,
.spread--text-image,
.spread--asymmetric {
  display: grid;
  gap: var(--s-4);
}

@media (min-width: 600px) {
  .spread--two-up { grid-template-columns: repeat(2, 1fr); }
}

@media (min-width: 1000px) {
  .spread--three-up { grid-template-columns: repeat(3, 1fr); }
  .spread--text-image { grid-template-columns: 2fr 3fr; align-items: start; }
  .spread--asymmetric { grid-template-columns: 2fr 3fr; align-items: start; }
}

/* Reduced motion: switch off the small hover transitions. */
@media (prefers-reduced-motion: reduce) {
  a:hover { opacity: 1; transition: none; }
  *, *::before, *::after { transition: none !important; animation: none !important; }
}

/* Skip link for keyboard users. */
.skip-link {
  position: absolute;
  left: -10000px;
  top: auto;
  width: 1px;
  height: 1px;
  overflow: hidden;
}
.skip-link:focus {
  position: fixed;
  left: var(--s-2);
  top: var(--s-2);
  width: auto;
  height: auto;
  padding: var(--s-1) var(--s-2);
  background: var(--bg);
  border: var(--rule-thin) solid var(--accent);
  z-index: 100;
}
```

- [ ] **Step 2: Sanity-check by writing a tiny scratch file**

Create a temporary scratch HTML at `_scratch.html` (gitignored — we delete it at the end of this task):

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>scratch</title>
  <link rel="stylesheet" href="styles/base.css">
</head>
<body>
  <main class="frame">
    <h1 class="t-hero">Chaziri Eleni</h1>
    <p class="t-hero-sub">Architect's Portfolio</p>
    <p class="t-hero-meta">2021–2025</p>
    <hr class="rule">
    <p>Body copy in Jost regular. The quick brown fox jumps over the lazy dog.</p>
    <p class="t-caption">Section A–A · 1:200</p>
  </main>
</body>
</html>
```

- [ ] **Step 3: Open the scratch page in a browser and verify**

Run: `xdg-open _scratch.html` (Linux) or `open _scratch.html` (macOS).

Expected:
- Hero text renders in Jost Bold, uppercased, with wide tracking.
- Sub line appears in deep blue-green (`#2C5F5C`).
- Body paragraph is in Jost Regular at ~16px on dark grey (`#3A3A3A`).
- Caption is small, light, uppercase, with extra tracking.
- A 1px hairline rule separates the header from the body text.

- [ ] **Step 4: Delete the scratch file**

Run: `rm _scratch.html`

- [ ] **Step 5: Commit**

```bash
git add styles/base.css
git commit -m "Add base.css: tokens, reset, type scale, layout primitives"
```

---

### Task 8: Create `styles/site.css` — header, nav, index, about

**Files:**
- Create: `styles/site.css`

Page-level styles for the header (used on every page), the index page, and the about page.

- [ ] **Step 1: Create the file**

Create `styles/site.css` with this content:

```css
/* ============================================================
   site.css — header, nav, index page, about page.
   Loaded after base.css.
   ============================================================ */

/* ---------- Header (every page) --------------------------- */

.site-header {
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bg);
  border-bottom: var(--rule-thin) solid var(--rule);
}

.site-header__inner {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--s-4);
  padding-block: var(--s-3);
}

.site-header__wordmark {
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3em;
  color: var(--ink);
  font-size: 0.9375rem;
  white-space: nowrap;
}

.site-nav {
  display: flex;
  gap: var(--s-4);
}

.site-nav a {
  color: var(--body);
  font-size: 0.875rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.site-nav a[aria-current="page"] {
  color: var(--ink);
  border-bottom: var(--rule-thin) solid var(--accent);
  padding-bottom: 2px;
}

/* ---------- Index hero ------------------------------------ */

.hero {
  position: relative;
  min-height: calc(100vh - 4rem);  /* viewport minus header */
  display: flex;
  align-items: flex-end;
  padding-block: var(--s-7);
}

/* Vertical hairline: starts at top of hero, ends at ~75% height. */
.hero::after {
  content: "";
  position: absolute;
  top: 0;
  bottom: 25%;
  right: 33%;
  width: 1px;
  background: var(--accent);
}

.hero__wordmark {
  /* Sits in the lower third, just left of the hairline (which is at 33% from right). */
  margin-right: 35%;
  margin-left: auto;
  text-align: right;
}

.hero__wordmark .t-hero { display: block; }
.hero__wordmark .t-hero-sub { display: block; margin-top: var(--s-2); }
.hero__wordmark .t-hero-meta { display: block; margin-top: var(--s-1); }

@media (max-width: 599px) {
  .hero::after { right: 8%; }
  .hero__wordmark { margin-right: 12%; }
}

/* ---------- Index statement ------------------------------- */

.statement {
  margin-block: var(--section-y);
  max-width: 50ch;
}

/* ---------- Index project grid ---------------------------- */

.work-grid {
  display: grid;
  gap: var(--s-5);
  margin-block: var(--section-y);
  grid-template-columns: 1fr;
}

@media (min-width: 600px) { .work-grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 1000px) { .work-grid { grid-template-columns: repeat(4, 1fr); } }

.work-card {
  display: block;
  color: inherit;
  text-align: center;
}

.work-card img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  background: var(--mute);
  transition: opacity 200ms ease;
}

.work-card__num {
  display: block;
  margin-top: var(--s-2);
  font-weight: 300;
  letter-spacing: 0.1em;
  color: var(--accent);
}

.work-card__title {
  display: block;
  margin-top: var(--s-1);
  font-weight: 400;
  color: var(--ink);
  transition: transform 300ms ease;
}

.work-card:hover img { opacity: 0.92; }
.work-card:hover .work-card__title { transform: translateY(-2px); }

/* ---------- Index about teaser ---------------------------- */

.about-teaser {
  margin-block: var(--section-y);
  max-width: 50ch;
}

.about-teaser a {
  font-weight: 400;
  border-bottom: var(--rule-thin) solid var(--accent);
  padding-bottom: 2px;
}

/* ---------- About page ------------------------------------ */

.about-header {
  margin-block: var(--section-y) var(--s-4);
}

.about-grid {
  display: grid;
  gap: var(--s-5);
  margin-block: var(--section-y);
  grid-template-columns: 1fr;
}

@media (min-width: 800px) {
  .about-grid { grid-template-columns: repeat(2, 1fr); }
}

.about-block h2 {
  font-size: 0.875rem;
  font-weight: 300;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: var(--s-2);
}

.about-block dl {
  margin: 0 0 var(--s-4);
}

.about-block dt {
  font-weight: 400;
  color: var(--ink);
  margin-top: var(--s-2);
}

.about-block dd {
  margin: 0;
  color: var(--body);
  font-size: 0.9375rem;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--s-1);
}

.skill-tags li {
  border: var(--rule-thin) solid var(--rule);
  padding: 4px 10px;
  font-size: 0.8125rem;
  font-weight: 300;
  color: var(--body);
}

.contact-block {
  margin-block: var(--section-y);
}

.contact-block dt {
  font-size: 0.75rem;
  font-weight: 300;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
  margin-top: var(--s-2);
}

.contact-block dd {
  margin: 0;
  font-size: 1.125rem;
}

.contact-block dd a {
  font-weight: 700;
}
```

- [ ] **Step 2: Commit**

```bash
git add styles/site.css
git commit -m "Add site.css: header, nav, index page, about page"
```

---

### Task 9: Create `styles/project.css` — project header, spread refinements, captions

**Files:**
- Create: `styles/project.css`

Adds project-page-specific styles on top of the spread primitives in `base.css`. Defines the project header, the `.drawing` wrapper for technical drawings on the muted background, the `.caption` placement, and the "next project" link.

- [ ] **Step 1: Create the file**

Create `styles/project.css` with this content:

```css
/* ============================================================
   project.css — project page header, drawing wrapper, captions,
   "next project" link.
   Loaded after base.css. Composes with .spread primitives.
   ============================================================ */

/* ---------- Project header -------------------------------- */

.project-header {
  margin-block: var(--section-y) var(--s-5);
}

.project-header__num {
  display: block;
  font-weight: 300;
  font-size: clamp(2.5rem, 6vw, 4rem);
  color: var(--accent);
  letter-spacing: 0.05em;
  line-height: 1;
}

.project-header__title {
  display: block;
  margin-top: var(--s-2);
  font-weight: 700;
  font-size: clamp(1.5rem, 3vw, 2rem);
  color: var(--ink);
}

.project-header__meta {
  display: block;
  margin-top: var(--s-1);
  color: var(--body);
  font-size: 0.9375rem;
}

.project-header__rule {
  border: 0;
  border-top: var(--rule-thin) solid var(--rule);
  margin-top: var(--s-3);
}

/* ---------- Drawing wrapper ------------------------------- */

/* Plans, sections, and other technical drawings sit on the muted background
   so they read as drawings — not renders — and so they don't compete
   visually with photographic renders adjacent to them. */
.drawing {
  background: var(--mute);
  padding: var(--s-3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.drawing img {
  width: 100%;
  height: auto;
}

/* ---------- Captions -------------------------------------- */

figure {
  margin: 0;
}

figure .caption,
figcaption {
  display: block;
  margin-top: var(--s-1);
  font-size: 0.8125rem;
  font-weight: 300;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--body);
}

/* ---------- Spread refinements ---------------------------- */

/* Inside .spread--text-image, the text column uses body type and
   wraps tightly; the image column fills its grid cell. */
.spread--text-image .text,
.spread--asymmetric .text {
  max-width: 62ch;
}

.spread--text-image img,
.spread--asymmetric img,
.spread--two-up img,
.spread--three-up img {
  width: 100%;
  height: auto;
}

/* When .spread--text-only is used inside a project page, centre it. */
.spread--text-only p { margin-inline: auto; }

/* ---------- Next-project link ----------------------------- */

.next-project {
  border-top: var(--rule-thin) solid var(--rule);
  margin-block: var(--section-y) var(--s-5);
  padding-top: var(--s-4);
  text-align: right;
}

.next-project a {
  font-size: 0.875rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--accent);
}
```

- [ ] **Step 2: Commit**

```bash
git add styles/project.css
git commit -m "Add project.css: project header, drawing wrapper, captions"
```

---


## Section 3 — Index & About pages (Tasks 10–11)

These two pages frame the project pages and exercise every primitive we've defined. They land before the project pages so the chrome (header, nav) and the global look are confirmed end-to-end before we go wide.

---

### Task 10: Build `index.html`

**Files:**
- Create: `index.html`

Implements §2 of the spec: header → hero (type-only, vertical hairline) → statement → 4-card "Selected Work" grid → about teaser. No footer.

- [ ] **Step 1: Look up the four hero image dimensions**

For each project's hero image (project-01/image-01, project-02/image-04, project-03/image-01, project-04/image-01), read the entry from `images/web/_manifest.json` and note the width/height. We'll use them to set `width`/`height` attributes on the `<img>` so the page does not shift as images load.

Run:

```bash
python3 -c "
import json
m = json.load(open('images/web/_manifest.json'))
for k in ['project-01/image-01', 'project-02/image-04', 'project-03/image-01', 'project-04/image-01']:
    print(k, m[k])
"
```

Expected: prints four lines like `project-01/image-01 {'width': 1535, 'height': 850}`. Substitute the real numbers into the `width`/`height` attributes below in step 2.

(Why these four heroes: image-01 is the title-page render for projects 01/03/04. Project 02's image-01 is a site plan, not a render — image-04 is the strongest exterior render in that project.)

- [ ] **Step 2: Create the file**

Create `index.html` with this content. **Replace `WIDTH`/`HEIGHT` placeholders with the real numbers from step 1** — they are the only values the engineer fills in:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Chaziri Eleni — Architect's Portfolio</title>
  <meta name="description" content="Portfolio of architect Chaziri Eleni: public space, restoration, and building design from concept to detailed delivery.">
  <link rel="stylesheet" href="styles/base.css">
  <link rel="stylesheet" href="styles/site.css">
  <link rel="preload" as="font" type="font/woff2" href="styles/fonts/jost-400.woff2" crossorigin>
</head>
<body>
  <a class="skip-link" href="#work">Skip to work</a>

  <header class="site-header">
    <div class="frame site-header__inner">
      <a class="site-header__wordmark" href="index.html">Chaziri Eleni</a>
      <nav class="site-nav" aria-label="Primary">
        <a href="index.html#work" aria-current="page">Work</a>
        <a href="about.html">About</a>
      </nav>
    </div>
  </header>

  <main id="main">
    <section class="hero">
      <div class="frame hero__wordmark">
        <span class="t-hero">Chaziri Eleni</span>
        <span class="t-hero-sub">Architect's Portfolio</span>
        <span class="t-hero-meta">2021–2025</span>
      </div>
    </section>

    <section class="frame statement">
      <p>An architect working across public space, restoration, and building design — from concept through detailed development and delivery. Based in Thessaloniki, available internationally.</p>
    </section>

    <section id="work" class="frame">
      <h1 class="t-h2" style="text-align:center; letter-spacing:0.12em; text-transform:uppercase; font-weight:300; color:var(--accent);">Selected Work</h1>
      <div class="work-grid">
        <a class="work-card" href="projects/01-xanthi-pavilion.html">
          <img src="images/web/project-01/image-01-400.jpg"
               srcset="images/web/project-01/image-01-400.jpg 400w,
                       images/web/project-01/image-01-800.jpg 800w"
               sizes="(min-width: 1000px) 25vw, (min-width: 600px) 50vw, 100vw"
               width="WIDTH" height="HEIGHT"
               alt="Exterior render of the Xanthi City Pavilion">
          <span class="work-card__num">01</span>
          <span class="work-card__title">Xanthi City Pavilion</span>
        </a>

        <a class="work-card" href="projects/02-tobacco-warehouse.html">
          <img src="images/web/project-02/image-04-400.jpg"
               srcset="images/web/project-02/image-04-400.jpg 400w,
                       images/web/project-02/image-04-800.jpg 800w"
               sizes="(min-width: 1000px) 25vw, (min-width: 600px) 50vw, 100vw"
               width="WIDTH" height="HEIGHT"
               alt="Restored tobacco warehouse on Nestos Street, Xanthi">
          <span class="work-card__num">02</span>
          <span class="work-card__title">Tobacco Warehouse, Xanthi</span>
        </a>

        <a class="work-card" href="projects/03-therma-spa.html">
          <img src="images/web/project-03/image-01-400.jpg"
               srcset="images/web/project-03/image-01-400.jpg 400w,
                       images/web/project-03/image-01-800.jpg 800w"
               sizes="(min-width: 1000px) 25vw, (min-width: 600px) 50vw, 100vw"
               width="WIDTH" height="HEIGHT"
               alt="Spa facilities and hospitality areas in Therma, Samothrace">
          <span class="work-card__num">03</span>
          <span class="work-card__title">Therma Spa, Samothrace</span>
        </a>

        <a class="work-card" href="projects/04-historic-restoration.html">
          <img src="images/web/project-04/image-01-400.jpg"
               srcset="images/web/project-04/image-01-400.jpg 400w,
                       images/web/project-04/image-01-800.jpg 800w"
               sizes="(min-width: 1000px) 25vw, (min-width: 600px) 50vw, 100vw"
               width="WIDTH" height="HEIGHT"
               alt="Restored facade of historic building">
          <span class="work-card__num">04</span>
          <span class="work-card__title">Historic Restoration</span>
        </a>
      </div>
    </section>

    <section class="frame about-teaser">
      <p>Member of the Technical Chamber of Greece. Currently a junior architect at OFFICE25ARCHITECTS, Thessaloniki. <a href="about.html">Read more →</a></p>
    </section>
  </main>
</body>
</html>
```

- [ ] **Step 3: Validate the markup**

Run: `tidy -q -e index.html`

Expected: prints either nothing, or only informational messages. No `Error:` or `warning:` lines. (If `tidy` is not installed: `sudo apt install tidy` on Debian/Ubuntu, `brew install tidy-html5` on macOS.)

- [ ] **Step 4: Open the page in a browser at three widths**

Run: `xdg-open index.html` (or `open index.html` on macOS).

Then in the browser dev tools, switch the viewport to:
1. **360px wide.** Expected: hero wordmark wraps comfortably; vertical hairline visible on the right; "Selected Work" grid stacks 1-up; no horizontal scroll.
2. **768px wide.** Expected: work grid is 2-up.
3. **1440px wide.** Expected: work grid is 4-up; hero wordmark is right-aligned; vertical hairline ends at ~75% of the hero height.

- [ ] **Step 5: Verify accessibility (Lighthouse)**

Open Chrome DevTools → Lighthouse → run an Accessibility audit on `index.html`.

Expected: Accessibility score is **100**. No contrast warnings. No "image without alt" warnings.

- [ ] **Step 6: Verify CLS ≈ 0**

In Chrome DevTools → Performance → reload with throttling enabled. Inspect the recorded timeline.

Expected: Cumulative Layout Shift score is `< 0.01` (i.e., images do not shift the page as they load — `width`/`height` attributes are doing their job).

- [ ] **Step 7: Commit**

```bash
git add index.html
git commit -m "Add index.html: hero, statement, work grid, about teaser"
```

---

### Task 11: Build `about.html`

**Files:**
- Create: `about.html`

Implements §5 of the spec: header → "About" page heading → profile statement → two-column grid (Experience & Education / Skills & Languages) → contact block with placeholder email and phone.

- [ ] **Step 1: Create the file**

Create `about.html` with this content. **Note the two `REPLACE-ME` placeholders in the contact block; those will be filled in by the user (not by the engineer) before deployment**:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>About — Chaziri Eleni</title>
  <meta name="description" content="Chaziri Eleni — architect based in Thessaloniki, working across public space, restoration, and building design.">
  <link rel="stylesheet" href="styles/base.css">
  <link rel="stylesheet" href="styles/site.css">
  <link rel="preload" as="font" type="font/woff2" href="styles/fonts/jost-400.woff2" crossorigin>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header">
    <div class="frame site-header__inner">
      <a class="site-header__wordmark" href="index.html">Chaziri Eleni</a>
      <nav class="site-nav" aria-label="Primary">
        <a href="index.html#work">Work</a>
        <a href="about.html" aria-current="page">About</a>
      </nav>
    </div>
  </header>

  <main id="main">
    <div class="frame">
      <header class="about-header">
        <h1 class="t-h1">About</h1>
        <hr class="rule">
      </header>

      <p>Architect based in Thessaloniki, working across public space, restoration, and building design. Member of the Technical Chamber of Greece. Currently a junior architect at OFFICE25ARCHITECTS.</p>

      <section class="about-grid" aria-label="Experience, education and skills">
        <div class="about-block">
          <h2>Experience</h2>
          <dl>
            <dt>09.2023 – present</dt>
            <dd>Junior Architect, OFFICE25ARCHITECTS · Thessaloniki, Greece</dd>
            <dt>07.2022 – 09.2022</dt>
            <dd>Intern, Akis Firoglanis Technical Office · Rhodes, Greece</dd>
          </dl>

          <h2>Education</h2>
          <dl>
            <dt>2017 – 2024</dt>
            <dd>Democritus University of Thrace · Architectural Engineering Department</dd>
          </dl>

          <h2>Seminars</h2>
          <dl>
            <dt>14.10.2020</dt>
            <dd>GSD1x: The Architectural Imagination · HarvardX</dd>
          </dl>
        </div>

        <div class="about-block">
          <h2>Technical Skills</h2>
          <ul class="skill-tags">
            <li>ArchiCAD</li>
            <li>AutoCAD</li>
            <li>Revit</li>
            <li>Lumion</li>
            <li>Twinmotion</li>
            <li>SketchUp</li>
            <li>3dsMax</li>
            <li>Photoshop</li>
            <li>InDesign</li>
            <li>Metashape</li>
            <li>Office365</li>
          </ul>

          <h2>Soft Skills</h2>
          <ul class="skill-tags">
            <li>Concept development</li>
            <li>Attention to detail</li>
            <li>Collaboration</li>
            <li>Presentation</li>
            <li>Adaptability</li>
            <li>Time management</li>
            <li>Historical &amp; cultural research</li>
          </ul>

          <h2>Languages</h2>
          <dl>
            <dt>English</dt>
            <dd>Fluent — IELTS 7.5 (2024), C2 EDI (2016)</dd>
            <dt>Italian</dt>
            <dd>Very good — C1 KPG</dd>
            <dt>Greek</dt>
            <dd>Native</dd>
          </dl>
        </div>
      </section>

      <hr class="rule">

      <section id="contact" class="contact-block" aria-label="Contact">
        <h2 class="t-h2" style="font-size:0.875rem; font-weight:300; letter-spacing:0.12em; text-transform:uppercase; color:var(--accent);">Contact</h2>
        <dl>
          <dt>Email</dt>
          <dd><a href="mailto:REPLACE-ME@example.com">REPLACE-ME@example.com</a></dd>
          <dt>Phone</dt>
          <dd><a href="tel:+00000000000">+00 000 000 000</a></dd>
          <dt>Location</dt>
          <dd>Thessaloniki, Greece</dd>
        </dl>
      </section>
    </div>
  </main>
</body>
</html>
```

- [ ] **Step 2: Validate the markup**

Run: `tidy -q -e about.html`

Expected: prints either nothing, or only informational messages. No `Error:` or `warning:` lines.

- [ ] **Step 3: Open the page in a browser and verify the layout**

Run: `xdg-open about.html`.

Then check the three viewport widths:
1. **360px.** Expected: experience and skills columns stack vertically; tag chips wrap; contact block is readable; no horizontal scroll.
2. **768px.** Expected: still single-column (the breakpoint is 800px). Tag chips lay out in a tidy row.
3. **1440px.** Expected: experience/education on the left, skills/languages on the right; contact block sits below at full width.

- [ ] **Step 4: Verify the contact placeholders are visible**

Read the rendered page. The Contact block must show:
- An email link reading `REPLACE-ME@example.com` with the `mailto:` href (so it is obviously a placeholder Eleni must replace before launch).
- A phone link reading `+00 000 000 000` with the `tel:` href.
- "Thessaloniki, Greece" as the location.

- [ ] **Step 5: Verify accessibility**

Open Chrome DevTools → Lighthouse → run an Accessibility audit on `about.html`.

Expected: Accessibility score is **100**. No contrast warnings. The form-controls / heading-order / landmark warnings should all be absent.

- [ ] **Step 6: Verify the header `aria-current` swap**

In the browser, on the About page, the "About" nav link should have an underline beneath it (the `aria-current="page"` style). The "Work" link should not. Open `index.html` and confirm the opposite is true.

- [ ] **Step 7: Commit**

```bash
git add about.html
git commit -m "Add about.html: profile, CV content, contact (#contact)"
```

---


## Section 4 — Project pages (Tasks 12–15)

One task per project. Each task creates a complete HTML page mirroring the corresponding PDF spreads, composing the `.spread*` primitives from `base.css` with the styles from `project.css`.

**A note on image-role verification:** The image filenames inside each project (`image-01.jpeg`, `image-02.jpeg`, …) reflect extraction order, not necessarily presentation order. The first step of every task is the same: open each image referenced in the page and confirm it matches the role the markup gives it. If a number is off (e.g., what the markup labels "exterior render" is actually a section drawing), swap the file references before validating.

**A note on the `width`/`height` attributes:** Every `<img>` needs `width` and `height` attributes set to the intrinsic dimensions from `images/web/_manifest.json`. The plan shows them as `width="W" height="H"` placeholders; replace them with real values during step 2.

**Helper command** for reading manifest values quickly. Run from the repo root:

```bash
python3 -c "
import json, sys
m = json.load(open('images/web/_manifest.json'))
for arg in sys.argv[1:]:
    print(f'{arg}: {m[arg]}')
" project-01/image-01 project-01/image-02 project-01/image-03
```

Adjust the trailing arguments to fetch the dimensions you need for each task.

---

### Task 12: Build `projects/01-xanthi-pavilion.html`

**Files:**
- Create: `projects/01-xanthi-pavilion.html`

11 images. PDF: pages 3–4. Layout map per spec §4: text-only intro → full hero → two-up interiors → asymmetric (volume sketches + section) → three-up plans → text-image (uses + masterplan) → two-up elevations.

- [ ] **Step 1: Verify image roles**

Open each image in `images/project-01/` and confirm:

| File              | Expected role on the page                    |
|-------------------|-----------------------------------------------|
| image-01.jpeg     | Hero exterior render (PDF p.3 large render)  |
| image-02.jpeg     | 4-quadrant volume sketches / axonometrics    |
| image-03.jpeg     | Interior render — corridor / hall            |
| image-04.jpeg     | Interior render — café / dining              |
| image-05.jpeg     | Plan A (PDF p.4 left)                        |
| image-06.jpeg     | Plan B (PDF p.4 middle)                      |
| image-07.jpeg     | Plan C (PDF p.4 right)                       |
| image-08.jpeg     | Long section drawing                         |
| image-09.jpeg     | Masterplan diagram                           |
| image-10.jpeg     | Short elevation/section A                    |
| image-11.jpeg     | Short elevation/section B                    |

If the actual image at any path differs from the role above, swap the filename in the markup of step 2 before validating.

- [ ] **Step 2: Look up dimensions**

Run: `python3 -c "import json; m=json.load(open('images/web/_manifest.json')); [print(f'project-01/image-{i:02d}', m[f'project-01/image-{i:02d}']) for i in range(1,12)]"`

Expected: prints 11 lines. Substitute the real `width`/`height` values into the `width="W" height="H"` placeholders in the markup below.

- [ ] **Step 3: Create the file**

Create `projects/01-xanthi-pavilion.html` with this content:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Xanthi City Pavilion — Chaziri Eleni</title>
  <meta name="description" content="A cultural centre for Xanthi: three volumes integrating leisure, cultural and commercial spaces around a public square.">
  <link rel="stylesheet" href="../styles/base.css">
  <link rel="stylesheet" href="../styles/project.css">
  <link rel="preload" as="font" type="font/woff2" href="../styles/fonts/jost-400.woff2" crossorigin>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header">
    <div class="frame site-header__inner">
      <a class="site-header__wordmark" href="../index.html">Chaziri Eleni</a>
      <nav class="site-nav" aria-label="Primary">
        <a href="../index.html#work" aria-current="page">Work</a>
        <a href="../about.html">About</a>
      </nav>
    </div>
  </header>

  <main id="main" class="frame">
    <article>
      <header class="project-header">
        <span class="project-header__num">01</span>
        <span class="project-header__title">Xanthi City Pavilion</span>
        <span class="project-header__meta">Cultural centre · Xanthi, Greece</span>
        <hr class="project-header__rule">
      </header>

      <section class="spread spread--text-only">
        <p>The synthesis is centered in the marketplace area of Xanthi, specifically where the fire department building stands today, near the Polytechnic University in the city's core.</p>
        <p><em>(pazari / παζάρι / {n} /pazári/)</em></p>
        <p>The proposal aims to rejuvenate and enhance the area through the establishment of a Cultural Centre, envisioned as an attraction for diverse age groups and a catalyst for economic, touristic and cultural development.</p>
        <p>The concept begins with the creation of a building that will serve as a landmark, integrating leisure, cultural and commercial spaces. The design comprises three volumes: two are positioned on the ground level, aligned with the site's topography, while the third volume functions as a bridge, seamlessly connecting the ground-floor structures.</p>
      </section>

      <section class="spread spread--full">
        <figure>
          <img src="../images/web/project-01/image-01-1600.jpg"
               srcset="../images/web/project-01/image-01-800.jpg 800w,
                       ../images/web/project-01/image-01-1600.jpg 1600w"
               sizes="(min-width: 1000px) 1400px, 100vw"
               width="W" height="H"
               fetchpriority="high"
               alt="Exterior render of the Xanthi City Pavilion: a low concrete volume with full-height glazing opening onto a paved public square.">
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <img src="../images/web/project-01/image-03-1600.jpg"
               srcset="../images/web/project-01/image-03-400.jpg 400w,
                       ../images/web/project-01/image-03-800.jpg 800w,
                       ../images/web/project-01/image-03-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Interior view of the covered walkway lined with timber-framed windows and pendant lighting.">
        </figure>
        <figure>
          <img src="../images/web/project-01/image-04-1600.jpg"
               srcset="../images/web/project-01/image-04-400.jpg 400w,
                       ../images/web/project-01/image-04-800.jpg 800w,
                       ../images/web/project-01/image-04-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Interior view of the café and reading area with long timber tables and full-height glazing.">
        </figure>
      </section>

      <section class="spread spread--asymmetric">
        <div class="text">
          <p>The design and arrangement of the volumes emphasize fluidity in all directions. Transparency of movement within and through the buildings was central to the concept, creating a clear and accessible flow across the site. A covered walkway extends from west to east, linking the plaza to a large green area across from the university campus.</p>
          <p>The core of the synthesis is a public square situated between the two ground-level volumes. An open-air cinema is incorporated adjacent to the square, following the site's natural elevations.</p>
        </div>
        <figure>
          <img src="../images/web/project-01/image-02-1600.jpg"
               srcset="../images/web/project-01/image-02-800.jpg 800w,
                       ../images/web/project-01/image-02-1600.jpg 1600w"
               sizes="(min-width: 1000px) 60vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Four-quadrant diagram showing volume axonometrics, axis lines, longitudinal section, and a circulation diagram of the three-volume composition.">
          <figcaption>Volume studies and circulation</figcaption>
        </figure>
      </section>

      <section class="spread spread--full">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-01/image-08-1600.jpg"
                 srcset="../images/web/project-01/image-08-800.jpg 800w,
                         ../images/web/project-01/image-08-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 1400px, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Long section through the three volumes showing the bridging upper volume connecting the two ground-level structures, with level annotations from +1.50 to +10.20 metres.">
          </div>
          <figcaption>Long section · Looking south</figcaption>
        </figure>
      </section>

      <section class="spread spread--three-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-01/image-05-1600.jpg"
                 srcset="../images/web/project-01/image-05-400.jpg 400w,
                         ../images/web/project-01/image-05-800.jpg 800w,
                         ../images/web/project-01/image-05-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Ground floor plan of the cultural centre showing reception, citizens' service centre and exhibition rooms.">
          </div>
          <figcaption>Ground floor</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-01/image-06-1600.jpg"
                 srcset="../images/web/project-01/image-06-400.jpg 400w,
                         ../images/web/project-01/image-06-800.jpg 800w,
                         ../images/web/project-01/image-06-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="First floor plan showing the catering hall and associated service areas.">
          </div>
          <figcaption>First floor</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-01/image-07-1600.jpg"
                 srcset="../images/web/project-01/image-07-400.jpg 400w,
                         ../images/web/project-01/image-07-800.jpg 800w,
                         ../images/web/project-01/image-07-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Second floor plan showing private functions, guest rooms and the multi-purpose hall.">
          </div>
          <figcaption>Second floor</figcaption>
        </figure>
      </section>

      <section class="spread spread--text-image">
        <div class="text">
          <h2 class="t-h2">Uses</h2>
          <p>On the ground floor, south of the primary study area, lies the complex's reception, including a Citizens Service Centre, information points, secretarial and management offices, a city exhibition and a small bar with seating areas.</p>
          <p>The next level features a catering hall with its associated service areas. The northern section houses additional showrooms and pavilions displaying local products and a mix of traditional and contemporary crafts.</p>
          <p>The third volume is dedicated to private functions: guest rooms and baths in the northern section, a multi-purpose hall in the southern section, linked by an outdoor bridge and walkway.</p>
        </div>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-01/image-09-1600.jpg"
                 srcset="../images/web/project-01/image-09-800.jpg 800w,
                         ../images/web/project-01/image-09-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 60vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Site masterplan showing the three pavilion volumes set within the surrounding urban fabric of Xanthi.">
          </div>
          <figcaption>Site plan · 1:500</figcaption>
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-01/image-10-1600.jpg"
                 srcset="../images/web/project-01/image-10-800.jpg 800w,
                         ../images/web/project-01/image-10-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Short section through the cultural centre.">
          </div>
          <figcaption>Section A–A</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-01/image-11-1600.jpg"
                 srcset="../images/web/project-01/image-11-800.jpg 800w,
                         ../images/web/project-01/image-11-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Short section showing the public square between the two ground-level volumes.">
          </div>
          <figcaption>Section B–B</figcaption>
        </figure>
      </section>

      <nav class="next-project frame" aria-label="Project navigation">
        <a href="02-tobacco-warehouse.html">Next project: Tobacco Warehouse →</a>
      </nav>
    </article>
  </main>
</body>
</html>
```

- [ ] **Step 4: Validate the markup**

Run: `tidy -q -e projects/01-xanthi-pavilion.html`

Expected: prints either nothing, or only informational messages. No `Error:` or `warning:` lines.

- [ ] **Step 5: Open in a browser at three widths**

Run: `xdg-open projects/01-xanthi-pavilion.html`.

Then check:
1. **360px.** Every spread stacks to one column. No horizontal scroll. Drawings sit on the muted grey background.
2. **768px.** Two-up spreads display as 2 columns; three-up still single-column (breakpoint 1000px). Plans are clearly drawings, not renders.
3. **1440px.** Three-up plans are 3 across; text-image is 40/60. Long section spans full width.

- [ ] **Step 6: Verify accessibility**

Open Chrome DevTools → Lighthouse → Accessibility audit on the project page.

Expected: Accessibility score is **100**. No contrast warnings. No missing-alt warnings.

- [ ] **Step 7: Verify CLS ≈ 0**

Chrome DevTools → Performance → reload with throttling.

Expected: Cumulative Layout Shift `< 0.01`. The page should not shift as images stream in.

- [ ] **Step 8: Commit**

```bash
git add projects/01-xanthi-pavilion.html
git commit -m "Add project page: Xanthi City Pavilion"
```

---

### Task 13: Build `projects/02-tobacco-warehouse.html`

**Files:**
- Create: `projects/02-tobacco-warehouse.html`

27 images (image-07 already excluded from `images/web/`). PDF: pages 5–10. The longest project. Layout map per spec §4: text-only intro → asymmetric urban context → two-up existing condition → asymmetric facade damage → two-up materials/preservation → text-only proposal → full restoration plan/sections → two-up interior renders × 2 → asymmetric proposal description + new building → full exterior renders.

- [ ] **Step 1: Verify image roles**

Open each image in `images/project-02/` (skip image-07 — excluded) and confirm:

| File              | Expected role on the page                                     |
|-------------------|---------------------------------------------------------------|
| image-01.png      | Urban site plan / context map                                 |
| image-02.jpeg     | Existing condition · west façade photogrammetry              |
| image-03.jpeg     | Existing condition · short section                            |
| image-04.jpeg     | **Hero exterior render** (also used on the index card)        |
| image-05.jpeg     | Existing condition · south façade photogrammetry             |
| image-06.jpeg     | Damage mapping · long façade                                  |
| image-07.jpeg     | EXCLUDED — do not reference                                   |
| image-08.jpeg     | Damage mapping · short façade                                 |
| image-09.jpeg     | Material identification · plan                                |
| image-10.jpeg     | Material identification · long section                        |
| image-11.jpeg     | Material identification · short section                       |
| image-12.jpeg     | Preservation status · plan                                    |
| image-13.jpeg     | Preservation status · long section                            |
| image-14.jpeg     | Preservation status · short section                           |
| image-15.jpeg     | Restoration plan · ground floor                               |
| image-16.jpeg     | Restoration plan · upper                                      |
| image-17.jpeg     | Restoration plan · roof                                       |
| image-18.jpeg     | Restoration · long section                                    |
| image-19.jpeg     | Restoration · short section                                   |
| image-20.jpeg     | Interior render · ground floor                                |
| image-21.jpeg     | Interior render · stair lobby                                 |
| image-22.jpeg     | Interior render · reading room                                |
| image-23.jpeg     | Interior render · roof glazing                                |
| image-24.jpeg     | New building · long elevation                                 |
| image-25.jpeg     | New building · short elevation                                |
| image-26.jpeg     | New building · roof plan with metal bridge                    |
| image-27.jpeg     | Exterior render · planted approach                            |
| image-28.jpeg     | Exterior render · landscape view                              |

If actual content differs from the role above, swap filenames in step 3 before validating.

- [ ] **Step 2: Look up dimensions**

Run: `python3 -c "import json; m=json.load(open('images/web/_manifest.json')); [print(f'project-02/image-{i:02d}', m.get(f'project-02/image-{i:02d}','MISSING')) for i in range(1,29)]"`

Expected: prints 28 lines. `project-02/image-07` should print `MISSING` (because we exclude it). All others present.

- [ ] **Step 3: Create the file**

Create `projects/02-tobacco-warehouse.html` with this content (W and H placeholders are filled in from step 2):

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tobacco Warehouse Restoration — Chaziri Eleni</title>
  <meta name="description" content="Restoration and adaptive reuse of a heritage tobacco warehouse on Nestos Street, Xanthi, as a digital library and reading room.">
  <link rel="stylesheet" href="../styles/base.css">
  <link rel="stylesheet" href="../styles/project.css">
  <link rel="preload" as="font" type="font/woff2" href="../styles/fonts/jost-400.woff2" crossorigin>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header">
    <div class="frame site-header__inner">
      <a class="site-header__wordmark" href="../index.html">Chaziri Eleni</a>
      <nav class="site-nav" aria-label="Primary">
        <a href="../index.html#work" aria-current="page">Work</a>
        <a href="../about.html">About</a>
      </nav>
    </div>
  </header>

  <main id="main" class="frame">
    <article>
      <header class="project-header">
        <span class="project-header__num">02</span>
        <span class="project-header__title">Restoration of the Tobacco Warehouse</span>
        <span class="project-header__meta">Heritage restoration · Nestos Street, Xanthi · Thesis project</span>
        <hr class="project-header__rule">
      </header>

      <section class="spread spread--text-only">
        <p>This thesis focuses on the restoration and reuse of a tobacco warehouse in the city of Xanthi.</p>
        <p>It is divided into four sections: a historical overview of the tobacco industry in Xanthi and an analysis of the city's urban fabric; documentation of the warehouse through photogrammetry and architectural drawings; an analysis of its current condition, materials, construction methods and preservation status; and a proposal to repurpose the building as a digital library and reading room.</p>
        <p>The tobacco warehouse, located in the centre of Xanthi, is a small rectangular building (10.50 m × 27 m) used primarily for tobacco storage. Despite being a single structure, it functioned as two separate spaces, indicated by dual entrances and an internal partition wall. In 2011, it was designated a heritage monument.</p>
      </section>

      <section class="spread spread--asymmetric">
        <div class="text">
          <h2 class="t-h2">Urban context</h2>
          <p>The warehouse sits in the dense urban fabric of central Xanthi. Its simple, symmetrical façades feature wooden windows with iron bars, stone staircases and skylights. The original dual-pitched wooden roof is no longer intact, leaving only the perimeter walls and partition.</p>
        </div>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-01-1600.jpg"
                 srcset="../images/web/project-02/image-01-800.jpg 800w,
                         ../images/web/project-02/image-01-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 60vw, 100vw"
                 width="W" height="H"
                 fetchpriority="high"
                 alt="Site plan showing the rectangular footprint of the tobacco warehouse within the surrounding urban grid of central Xanthi.">
          </div>
          <figcaption>Site plan · 1:1000</figcaption>
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-02-1600.jpg"
                 srcset="../images/web/project-02/image-02-800.jpg 800w,
                         ../images/web/project-02/image-02-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Photogrammetric drawing of the west façade showing the existing brick masonry condition, with weathered plaster, wooden window frames and external iron bars.">
          </div>
          <figcaption>Existing condition · West façade</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-03-1600.jpg"
                 srcset="../images/web/project-02/image-03-800.jpg 800w,
                         ../images/web/project-02/image-03-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Existing-condition short section through the warehouse showing the collapsed mezzanine and partition wall.">
          </div>
          <figcaption>Existing condition · Section</figcaption>
        </figure>
      </section>

      <section class="spread spread--full">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-05-1600.jpg"
                 srcset="../images/web/project-02/image-05-800.jpg 800w,
                         ../images/web/project-02/image-05-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 1400px, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Photogrammetric drawing of the south façade showing existing condition: regular fenestration with wooden windows, weathered plaster and stone foundation.">
          </div>
          <figcaption>Existing condition · South façade</figcaption>
        </figure>
      </section>

      <section class="spread spread--asymmetric">
        <div class="text">
          <h2 class="t-h2">Damage analysis</h2>
          <p>The current condition of the building is documented and classified through a damage-mapping legend. The western and southern façades, as well as the interior walls, are coated with lime plaster featuring drawn ornamentation over a brick substrate.</p>
          <p>Identified damage includes loss of original door, moisture ingress, loss or damage of glazing, staining due to metal oxidation, oxidation of metallic elements, vegetation growth, vandalism and graffiti, peeling and bulging plaster, and loss of stone-masonry surface.</p>
        </div>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-06-1600.jpg"
                 srcset="../images/web/project-02/image-06-800.jpg 800w,
                         ../images/web/project-02/image-06-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 60vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Damage-mapping drawing of the long south façade with colour-coded annotations for moisture ingress, plaster loss, vegetation growth and other damage categories.">
          </div>
          <figcaption>Damage mapping · South façade</figcaption>
        </figure>
      </section>

      <section class="spread spread--full">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-08-1600.jpg"
                 srcset="../images/web/project-02/image-08-800.jpg 800w,
                         ../images/web/project-02/image-08-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 1400px, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Damage-mapping drawing of the short west façade with the same colour-coded annotation system.">
          </div>
          <figcaption>Damage mapping · West façade</figcaption>
        </figure>
      </section>

      <section class="spread spread--three-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-09-1600.jpg"
                 srcset="../images/web/project-02/image-09-800.jpg 800w,
                         ../images/web/project-02/image-09-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Material identification plan showing lime-mortared rubble masonry, brick masonry, concrete and lime plaster surfaces.">
          </div>
          <figcaption>Materials · Plan</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-10-1600.jpg"
                 srcset="../images/web/project-02/image-10-800.jpg 800w,
                         ../images/web/project-02/image-10-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Material identification long section, colour-coded for masonry, plaster, wooden frames, stone staircases and external metal bars.">
          </div>
          <figcaption>Materials · Section</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-11-1600.jpg"
                 srcset="../images/web/project-02/image-11-800.jpg 800w,
                         ../images/web/project-02/image-11-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Material identification short section showing the partition wall and stair construction.">
          </div>
          <figcaption>Materials · Cross-section</figcaption>
        </figure>
      </section>

      <section class="spread spread--three-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-12-1600.jpg"
                 srcset="../images/web/project-02/image-12-800.jpg 800w,
                         ../images/web/project-02/image-12-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Preservation status plan classifying surfaces as well-preserved, fair, or showing absence of flooring or floor slab.">
          </div>
          <figcaption>Preservation · Plan</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-13-1600.jpg"
                 srcset="../images/web/project-02/image-13-800.jpg 800w,
                         ../images/web/project-02/image-13-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Preservation status long section using the same classification system.">
          </div>
          <figcaption>Preservation · Section</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-14-1600.jpg"
                 srcset="../images/web/project-02/image-14-800.jpg 800w,
                         ../images/web/project-02/image-14-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Preservation status short section.">
          </div>
          <figcaption>Preservation · Cross-section</figcaption>
        </figure>
      </section>

      <section class="spread spread--text-only">
        <h2 class="t-h2">Restoration and Adaptive Reuse Proposal</h2>
        <p>Research revealed that the local community undervalues the cultural significance of the tobacco warehouses, resulting in inadequate preservation efforts. This realization inspired the thesis, aimed at revitalizing a historic warehouse to enrich the area's cultural fabric and educational legacy.</p>
        <p>The proposal for a Digital Library and Reading Room emerged from the need for infrastructure to support Xanthi's university students. Libraries, often designed to blend organically with their surroundings, have evolved alongside electronic media — adapting and embracing digital functions while maintaining their role as cultural landmarks.</p>
        <p>Roof replacement: the old wooden trusses and Byzantine tiles are replaced with a glass roof, raised by 80 cm to ensure sufficient height for the upper floor and covered with two movable shading panels supported by metal frames. The main entrance is located on the southern façade at +1.30 m, with the reception and waiting area on the left and the stairwell on the right.</p>
      </section>

      <section class="spread spread--three-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-15-1600.jpg"
                 srcset="../images/web/project-02/image-15-800.jpg 800w,
                         ../images/web/project-02/image-15-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Restoration plan at ground floor level showing the new digital library layout integrated with the existing partition wall.">
          </div>
          <figcaption>Restoration · Ground floor</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-16-1600.jpg"
                 srcset="../images/web/project-02/image-16-800.jpg 800w,
                         ../images/web/project-02/image-16-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Restoration plan at upper floor level with three reading rooms accommodated under the new glazed roof.">
          </div>
          <figcaption>Restoration · Upper floor</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-17-1600.jpg"
                 srcset="../images/web/project-02/image-17-800.jpg 800w,
                         ../images/web/project-02/image-17-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Restoration roof plan showing the new glazed roof with shading panels and connection to the new building addition.">
          </div>
          <figcaption>Restoration · Roof plan</figcaption>
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-18-1600.jpg"
                 srcset="../images/web/project-02/image-18-800.jpg 800w,
                         ../images/web/project-02/image-18-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Restoration long section through the warehouse showing the new glazed roof, reading rooms and connection to the new addition.">
          </div>
          <figcaption>Restoration · Long section</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-19-1600.jpg"
                 srcset="../images/web/project-02/image-19-800.jpg 800w,
                         ../images/web/project-02/image-19-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Restoration short section through the partition wall showing the new opening at +1.30 m and the basement reading room.">
          </div>
          <figcaption>Restoration · Cross-section</figcaption>
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <img src="../images/web/project-02/image-20-1600.jpg"
               srcset="../images/web/project-02/image-20-400.jpg 400w,
                       ../images/web/project-02/image-20-800.jpg 800w,
                       ../images/web/project-02/image-20-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Interior render at ground floor showing exposed brick partition, timber flooring and tall arched windows.">
        </figure>
        <figure>
          <img src="../images/web/project-02/image-21-1600.jpg"
               srcset="../images/web/project-02/image-21-400.jpg 400w,
                       ../images/web/project-02/image-21-800.jpg 800w,
                       ../images/web/project-02/image-21-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Interior render of the stair lobby with the new metal stairwell and glazed roof above.">
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <img src="../images/web/project-02/image-22-1600.jpg"
               srcset="../images/web/project-02/image-22-400.jpg 400w,
                       ../images/web/project-02/image-22-800.jpg 800w,
                       ../images/web/project-02/image-22-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Interior render of an upper-floor reading room with timber tables and views through the arched windows.">
        </figure>
        <figure>
          <img src="../images/web/project-02/image-23-1600.jpg"
               srcset="../images/web/project-02/image-23-400.jpg 400w,
                       ../images/web/project-02/image-23-800.jpg 800w,
                       ../images/web/project-02/image-23-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Interior render under the new glazed roof showing the reading room with shading panels overhead.">
        </figure>
      </section>

      <section class="spread spread--asymmetric">
        <div class="text">
          <h2 class="t-h2">New Building Addition</h2>
          <p>Two new openings in the northern façade — at +1.30 m and +4.10 m — connect the warehouse with the surrounding area and the new building via a metal bridge. The new building consists of two volumes: a ground floor and a two-storey structure, designed in harmony with the warehouse.</p>
          <p>The ground-floor volume houses administration offices and a meeting room. The two-storey volume houses the digital library and reading room on both floors. A metal bridge bisects the two new buildings and connects them. The façades of the new buildings are simple, using vertical blinds for controlled shading.</p>
          <p>A shared basement between the two new volumes contains storage, restrooms for administration and visitors, and a boiler room.</p>
        </div>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-24-1600.jpg"
                 srcset="../images/web/project-02/image-24-800.jpg 800w,
                         ../images/web/project-02/image-24-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 60vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Long elevation of the new building addition alongside the restored warehouse.">
          </div>
          <figcaption>New building · Long elevation</figcaption>
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-25-1600.jpg"
                 srcset="../images/web/project-02/image-25-800.jpg 800w,
                         ../images/web/project-02/image-25-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Short elevation of the two-storey volume showing vertical blinds for shading.">
          </div>
          <figcaption>New building · Short elevation</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-02/image-26-1600.jpg"
                 srcset="../images/web/project-02/image-26-800.jpg 800w,
                         ../images/web/project-02/image-26-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Roof plan showing the metal bridge connecting the two new volumes.">
          </div>
          <figcaption>New building · Roof plan</figcaption>
        </figure>
      </section>

      <section class="spread spread--full">
        <figure>
          <img src="../images/web/project-02/image-04-1600.jpg"
               srcset="../images/web/project-02/image-04-800.jpg 800w,
                       ../images/web/project-02/image-04-1600.jpg 1600w"
               sizes="(min-width: 1000px) 1400px, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Hero exterior render of the restored warehouse alongside the new building addition, with planted approach in the foreground.">
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <img src="../images/web/project-02/image-27-1600.jpg"
               srcset="../images/web/project-02/image-27-400.jpg 400w,
                       ../images/web/project-02/image-27-800.jpg 800w,
                       ../images/web/project-02/image-27-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Exterior render showing the planted garden approach to the new building addition.">
        </figure>
        <figure>
          <img src="../images/web/project-02/image-28-1600.jpg"
               srcset="../images/web/project-02/image-28-400.jpg 400w,
                       ../images/web/project-02/image-28-800.jpg 800w,
                       ../images/web/project-02/image-28-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Wider landscape view of the restored warehouse complex within its urban context.">
        </figure>
      </section>

      <nav class="next-project frame" aria-label="Project navigation">
        <a href="03-therma-spa.html">Next project: Therma Spa →</a>
      </nav>
    </article>
  </main>
</body>
</html>
```

- [ ] **Step 4: Validate the markup**

Run: `tidy -q -e projects/02-tobacco-warehouse.html`

Expected: prints either nothing, or only informational messages. No `Error:` or `warning:` lines.

- [ ] **Step 5: Confirm image-07 is not referenced**

Run: `grep -n 'image-07' projects/02-tobacco-warehouse.html`

Expected: no output. (The file must not reference the excluded image anywhere.)

- [ ] **Step 6: Open in a browser at three widths**

Run: `xdg-open projects/02-tobacco-warehouse.html`.

Then check 360px / 768px / 1440px viewports as in Task 12. Specifically watch for:
- The four three-up rows of plans/sections render as 3 columns on desktop, 1 column on mobile.
- Drawings sit on the muted grey background; renders sit on white.
- The page scrolls without horizontal overflow at 360px.
- Total page weight stays under 3 MB on initial load (Network tab → Disable cache → reload). Lazy loading should keep it well below this for the visible viewport.

- [ ] **Step 7: Verify accessibility and CLS**

Lighthouse Accessibility audit: must be **100**. Performance tab CLS: `< 0.01`.

- [ ] **Step 8: Commit**

```bash
git add projects/02-tobacco-warehouse.html
git commit -m "Add project page: Tobacco Warehouse Restoration"
```

---


### Task 14: Build `projects/03-therma-spa.html`

**Files:**
- Create: `projects/03-therma-spa.html`

10 images. PDF: pages 11–12. Layout map per spec §4: text-only intro → text-image (concept + main section) → two-up sections → two-up renders → full hero render → two-up landscape views.

- [ ] **Step 1: Verify image roles**

Open each image in `images/project-03/` and confirm:

| File              | Expected role on the page                              |
|-------------------|--------------------------------------------------------|
| image-01.jpeg     | Hero exterior render (main composition)                |
| image-02.jpeg     | Concept render · pool view                             |
| image-03.jpeg     | Long site section · upper                              |
| image-04.jpeg     | Long site section · lower                              |
| image-05.jpeg     | Render · landscape with hill                           |
| image-06.jpeg     | Render · pool deck                                     |
| image-07.jpeg     | Render · pool perspective                              |
| image-08.jpeg     | Interior render · glazed pool hall                     |
| image-09.jpeg     | Long elevation · upper                                 |
| image-10.jpeg     | Long elevation · lower                                 |

If actual content differs from the role above, swap filenames in step 3 before validating.

- [ ] **Step 2: Look up dimensions**

Run: `python3 -c "import json; m=json.load(open('images/web/_manifest.json')); [print(f'project-03/image-{i:02d}', m[f'project-03/image-{i:02d}']) for i in range(1,11)]"`

Expected: prints 10 lines. Substitute the real `width`/`height` values into the placeholders below.

- [ ] **Step 3: Create the file**

Create `projects/03-therma-spa.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Therma Spa — Chaziri Eleni</title>
  <meta name="description" content="Spa facilities and hospitality areas in Therma, Samothrace: a modular composition stepped across the natural terrain.">
  <link rel="stylesheet" href="../styles/base.css">
  <link rel="stylesheet" href="../styles/project.css">
  <link rel="preload" as="font" type="font/woff2" href="../styles/fonts/jost-400.woff2" crossorigin>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header">
    <div class="frame site-header__inner">
      <a class="site-header__wordmark" href="../index.html">Chaziri Eleni</a>
      <nav class="site-nav" aria-label="Primary">
        <a href="../index.html#work" aria-current="page">Work</a>
        <a href="../about.html">About</a>
      </nav>
    </div>
  </header>

  <main id="main" class="frame">
    <article>
      <header class="project-header">
        <span class="project-header__num">03</span>
        <span class="project-header__title">Spa facilities &amp; hospitality areas</span>
        <span class="project-header__meta">Wellness centre · Therma, Samothrace</span>
        <hr class="project-header__rule">
      </header>

      <section class="spread spread--text-only">
        <p>The composite concept was carefully developed within the natural landscape of Therma, Samothrace, with an emphasis on respecting and enhancing the site's unique character.</p>
        <p>Extensive research and analysis of the area informed key design objectives, including the use of simple, minimalistic forms, tranquil lines, a modular cellular structure and a progression across multiple levels.</p>
        <p>These guiding principles inspired the creation of spa facilities, a wellness center, and hospitality spaces that blend harmoniously with the natural terrain and atmosphere of Therma.</p>
      </section>

      <section class="spread spread--text-image">
        <div class="text">
          <h2 class="t-h2">Three volumes, one site</h2>
          <p>The facilities are organized into three distinct architectural volumes, each dedicated to a specific programmatic function. This arrangement allows each volume to operate autonomously, ensuring efficient functionality, while the unified design language creates a cohesive whole that is visually and spatially integrated.</p>
          <p>The result is an architectural composition that balances independence and unity, seamlessly connecting the building's uses to both the surrounding environment and to one another.</p>
        </div>
        <figure>
          <img src="../images/web/project-03/image-01-1600.jpg"
               srcset="../images/web/project-03/image-01-800.jpg 800w,
                       ../images/web/project-03/image-01-1600.jpg 1600w"
               sizes="(min-width: 1000px) 60vw, 100vw"
               width="W" height="H"
               fetchpriority="high"
               alt="Concept render showing the three spa volumes stepping down the hillside above Therma, Samothrace, with the pool deck in the foreground.">
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-03/image-03-1600.jpg"
                 srcset="../images/web/project-03/image-03-800.jpg 800w,
                         ../images/web/project-03/image-03-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Long site section through the spa complex showing the cascading volumes embedded in the terrain.">
          </div>
          <figcaption>Site section · Upper</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-03/image-04-1600.jpg"
                 srcset="../images/web/project-03/image-04-800.jpg 800w,
                         ../images/web/project-03/image-04-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Long site section showing the lower terraces, pool deck and connection to the natural slope.">
          </div>
          <figcaption>Site section · Lower</figcaption>
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <img src="../images/web/project-03/image-02-1600.jpg"
               srcset="../images/web/project-03/image-02-400.jpg 400w,
                       ../images/web/project-03/image-02-800.jpg 800w,
                       ../images/web/project-03/image-02-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Render of the wellness volume with full-height glazing onto the outdoor pool.">
        </figure>
        <figure>
          <img src="../images/web/project-03/image-08-1600.jpg"
               srcset="../images/web/project-03/image-08-400.jpg 400w,
                       ../images/web/project-03/image-08-800.jpg 800w,
                       ../images/web/project-03/image-08-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Interior render of the glazed pool hall with stepped seating and views to the surrounding hills.">
        </figure>
      </section>

      <section class="spread spread--full">
        <figure>
          <img src="../images/web/project-03/image-05-1600.jpg"
               srcset="../images/web/project-03/image-05-800.jpg 800w,
                       ../images/web/project-03/image-05-1600.jpg 1600w"
               sizes="(min-width: 1000px) 1400px, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Wide landscape render of the spa complex set against the green hill of Therma, with a stretched pool deck running parallel to the volumes.">
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <img src="../images/web/project-03/image-06-1600.jpg"
               srcset="../images/web/project-03/image-06-400.jpg 400w,
                       ../images/web/project-03/image-06-800.jpg 800w,
                       ../images/web/project-03/image-06-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Render of the pool deck and surrounding terrace with sun loungers.">
        </figure>
        <figure>
          <img src="../images/web/project-03/image-07-1600.jpg"
               srcset="../images/web/project-03/image-07-400.jpg 400w,
                       ../images/web/project-03/image-07-800.jpg 800w,
                       ../images/web/project-03/image-07-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Closer perspective of the pool with the spa volumes rising behind it.">
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-03/image-09-1600.jpg"
                 srcset="../images/web/project-03/image-09-800.jpg 800w,
                         ../images/web/project-03/image-09-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Long elevation showing the upper portion of the cascading spa volumes against the hillside.">
          </div>
          <figcaption>Elevation · Upper</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-03/image-10-1600.jpg"
                 srcset="../images/web/project-03/image-10-800.jpg 800w,
                         ../images/web/project-03/image-10-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Long elevation showing the lower portion of the spa volumes and the pool deck terrace.">
          </div>
          <figcaption>Elevation · Lower</figcaption>
        </figure>
      </section>

      <nav class="next-project frame" aria-label="Project navigation">
        <a href="04-historic-restoration.html">Next project: Historic Restoration →</a>
      </nav>
    </article>
  </main>
</body>
</html>
```

- [ ] **Step 4: Validate the markup**

Run: `tidy -q -e projects/03-therma-spa.html`

Expected: prints either nothing, or only informational messages. No `Error:` or `warning:` lines.

- [ ] **Step 5: Open in a browser at three widths**

Run: `xdg-open projects/03-therma-spa.html`. Verify 360px / 768px / 1440px as in Task 12.

- [ ] **Step 6: Verify accessibility and CLS**

Lighthouse Accessibility: **100**. Performance CLS: `< 0.01`.

- [ ] **Step 7: Commit**

```bash
git add projects/03-therma-spa.html
git commit -m "Add project page: Therma Spa"
```

---

### Task 15: Build `projects/04-historic-restoration.html`

**Files:**
- Create: `projects/04-historic-restoration.html`

12 images. PDF: pages 13–14. Layout map per spec §4: text-only principles → text-image (intervention principles + restored façade) → two-up (decorative pattern study) → asymmetric (interior renders + new uses diagrams) → text-image (program + restored exterior) → two-up final renders.

- [ ] **Step 1: Verify image roles**

Open each image in `images/project-04/` and confirm:

| File              | Expected role on the page                              |
|-------------------|--------------------------------------------------------|
| image-01.jpeg     | Restored south façade elevation                        |
| image-02.jpeg     | Pattern completion · ornamental detail                 |
| image-03.jpeg     | Original witnesses · ornamental fragments              |
| image-04.jpeg     | Interior render · reading room with arched windows     |
| image-05.jpeg     | Interior render · open studio with arches              |
| image-06.jpeg     | New uses diagram · ground floor                        |
| image-07.jpeg     | New uses diagram · first floor                         |
| image-08.jpeg     | New uses diagram · attic                               |
| image-09.jpeg     | Restored long façade elevation                         |
| image-10.jpeg     | Restored short façade with stair                       |
| image-11.jpeg     | Final interior render · finished space                 |
| image-12.jpeg     | Final interior render · finished space, alternate view |

If actual content differs from the role above, swap filenames in step 3 before validating.

- [ ] **Step 2: Look up dimensions**

Run: `python3 -c "import json; m=json.load(open('images/web/_manifest.json')); [print(f'project-04/image-{i:02d}', m[f'project-04/image-{i:02d}']) for i in range(1,13)]"`

Expected: prints 12 lines. Substitute real `width`/`height` values into placeholders below.

- [ ] **Step 3: Create the file**

Create `projects/04-historic-restoration.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Historic Restoration — Chaziri Eleni</title>
  <meta name="description" content="Restoration, redesign and reuse of a historic building: a careful balance between preservation of authenticity and contemporary adaptation.">
  <link rel="stylesheet" href="../styles/base.css">
  <link rel="stylesheet" href="../styles/project.css">
  <link rel="preload" as="font" type="font/woff2" href="../styles/fonts/jost-400.woff2" crossorigin>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header">
    <div class="frame site-header__inner">
      <a class="site-header__wordmark" href="../index.html">Chaziri Eleni</a>
      <nav class="site-nav" aria-label="Primary">
        <a href="../index.html#work" aria-current="page">Work</a>
        <a href="../about.html">About</a>
      </nav>
    </div>
  </header>

  <main id="main" class="frame">
    <article>
      <header class="project-header">
        <span class="project-header__num">04</span>
        <span class="project-header__title">Restoration, Redesign &amp; Reuse</span>
        <span class="project-header__meta">Historic building · Adaptive reuse for academic community</span>
        <hr class="project-header__rule">
      </header>

      <section class="spread spread--text-only">
        <h2 class="t-h2">Principles of Intervention</h2>
        <p>In restoring, adapting, and reactivating the historic building under study, the design approach prioritizes both the preservation of its historical and aesthetic value and its adaptation for contemporary use. The interventions were guided by a rigorous evaluation of the building's architectural integrity and its intended new functions.</p>
        <p>Selective reversal of alterations: removing or correcting modifications that detract from the building's authenticity. Historical conservation: retaining significant features, including later valuable additions, to preserve identity. Targeted restoration: partially restoring original typology, form and materials. Balanced interventions: bold changes where permissible, restraint where required. Modern adaptation: reconfiguring spaces to meet contemporary urban and visitor needs. Contrasts in design: highlighting the dynamic interplay between historical preservation and modern requirements.</p>
      </section>

      <section class="spread spread--text-image">
        <div class="text">
          <h2 class="t-h2">Programmatic objectives</h2>
          <p>This approach to intervention respects the building's historical fabric while thoughtfully integrating new functions, resulting in a sensitive yet dynamic reactivation that honors its heritage while ensuring relevance for the future.</p>
          <p>The proposed restoration and adaptive reuse address community needs for accessible gathering spaces and essential storage. The first-floor library will offer a rich resource of materials and a tranquil study environment, while the attic studios create specialized workspaces that respond to current overcrowding issues in the Architecture Department, where temporary design studios have been set up in general classrooms.</p>
        </div>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-04/image-01-1600.jpg"
                 srcset="../images/web/project-04/image-01-800.jpg 800w,
                         ../images/web/project-04/image-01-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 60vw, 100vw"
                 width="W" height="H"
                 fetchpriority="high"
                 alt="Restored south façade elevation showing the original neoclassical composition with its arched windows, balconies and stone-rusticated ground floor.">
          </div>
          <figcaption>Restored south façade</figcaption>
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-04/image-02-1600.jpg"
                 srcset="../images/web/project-04/image-02-800.jpg 800w,
                         ../images/web/project-04/image-02-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Pattern completion drawing reconstructing the original ornamental motif around an arched window opening from surviving fragments.">
          </div>
          <figcaption>Pattern completion</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-04/image-03-1600.jpg"
                 srcset="../images/web/project-04/image-03-800.jpg 800w,
                         ../images/web/project-04/image-03-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Photographs of surviving ornamental fragments — the 'original witnesses' that informed the pattern reconstruction.">
          </div>
          <figcaption>Original witnesses</figcaption>
        </figure>
      </section>

      <section class="spread spread--asymmetric">
        <div class="text">
          <h2 class="t-h2">New uses</h2>
          <p>Ground floor: dedicated to a printing and laser area, materials storage, cafeteria, general storage, and restroom facilities.</p>
          <p>First floor: designed as a library with an extensive selection of books for reading and borrowing, complemented by a study area, a self-contained kitchen, and restrooms.</p>
          <p>Attic: envisioned as a series of design studios for individual, group, and thesis work, along with a rest area to accommodate the significant hours students spend in studio work.</p>
        </div>
        <figure>
          <img src="../images/web/project-04/image-04-1600.jpg"
               srcset="../images/web/project-04/image-04-400.jpg 400w,
                       ../images/web/project-04/image-04-800.jpg 800w,
                       ../images/web/project-04/image-04-1600.jpg 1600w"
               sizes="(min-width: 1000px) 60vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Interior render of a reading room with deep blue ceiling, custom timber bookshelves and a row of arched windows.">
        </figure>
      </section>

      <section class="spread spread--three-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-04/image-06-1600.jpg"
                 srcset="../images/web/project-04/image-06-800.jpg 800w,
                         ../images/web/project-04/image-06-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Ground-floor diagram showing primary, secondary and ancillary uses colour-coded across the plan.">
          </div>
          <figcaption>Ground floor uses</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-04/image-07-1600.jpg"
                 srcset="../images/web/project-04/image-07-800.jpg 800w,
                         ../images/web/project-04/image-07-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="First-floor diagram showing the new library plan with study area and kitchen.">
          </div>
          <figcaption>First floor uses</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-04/image-08-1600.jpg"
                 srcset="../images/web/project-04/image-08-800.jpg 800w,
                         ../images/web/project-04/image-08-1600.jpg 1600w"
                 sizes="(min-width: 1000px) 33vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Attic diagram showing the new design studios and rest area.">
          </div>
          <figcaption>Attic uses</figcaption>
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <div class="drawing">
            <img src="../images/web/project-04/image-09-1600.jpg"
                 srcset="../images/web/project-04/image-09-800.jpg 800w,
                         ../images/web/project-04/image-09-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Restored long façade elevation showing the original neoclassical fenestration and the integrated new entrance.">
          </div>
          <figcaption>Restored long façade</figcaption>
        </figure>
        <figure>
          <div class="drawing">
            <img src="../images/web/project-04/image-10-1600.jpg"
                 srcset="../images/web/project-04/image-10-800.jpg 800w,
                         ../images/web/project-04/image-10-1600.jpg 1600w"
                 sizes="(min-width: 600px) 50vw, 100vw"
                 width="W" height="H"
                 loading="lazy"
                 alt="Restored short façade showing the secondary entrance and the new external stair connection.">
          </div>
          <figcaption>Restored short façade</figcaption>
        </figure>
      </section>

      <section class="spread spread--two-up">
        <figure>
          <img src="../images/web/project-04/image-05-1600.jpg"
               srcset="../images/web/project-04/image-05-400.jpg 400w,
                       ../images/web/project-04/image-05-800.jpg 800w,
                       ../images/web/project-04/image-05-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Interior render of an open studio space with the original arched windows preserved and a contemporary timber ceiling.">
        </figure>
        <figure>
          <img src="../images/web/project-04/image-11-1600.jpg"
               srcset="../images/web/project-04/image-11-400.jpg 400w,
                       ../images/web/project-04/image-11-800.jpg 800w,
                       ../images/web/project-04/image-11-1600.jpg 1600w"
               sizes="(min-width: 600px) 50vw, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Final interior render of the restored library space with arched windows and a custom seating arrangement.">
        </figure>
      </section>

      <section class="spread spread--full">
        <figure>
          <img src="../images/web/project-04/image-12-1600.jpg"
               srcset="../images/web/project-04/image-12-800.jpg 800w,
                       ../images/web/project-04/image-12-1600.jpg 1600w"
               sizes="(min-width: 1000px) 1400px, 100vw"
               width="W" height="H"
               loading="lazy"
               alt="Wider final interior render showing the connection between the restored historic envelope and the contemporary insertions.">
        </figure>
      </section>

      <nav class="next-project frame" aria-label="Project navigation">
        <a href="01-xanthi-pavilion.html">Next project: Xanthi City Pavilion →</a>
      </nav>
    </article>
  </main>
</body>
</html>
```

- [ ] **Step 4: Validate the markup**

Run: `tidy -q -e projects/04-historic-restoration.html`

Expected: prints either nothing, or only informational messages. No `Error:` or `warning:` lines.

- [ ] **Step 5: Open in a browser at three widths**

Run: `xdg-open projects/04-historic-restoration.html`. Verify 360px / 768px / 1440px as in Task 12.

- [ ] **Step 6: Verify accessibility and CLS**

Lighthouse Accessibility: **100**. Performance CLS: `< 0.01`.

- [ ] **Step 7: Verify the cyclic next link**

The "Next project" link at the bottom of project 04 must point to `01-xanthi-pavilion.html` (cyclic loop back to the first project per spec §4).

Run: `grep "next project" -i projects/04-historic-restoration.html`

Expected: shows the link text and `01-xanthi-pavilion.html` in the href.

- [ ] **Step 8: Commit**

```bash
git add projects/04-historic-restoration.html
git commit -m "Add project page: Historic Restoration"
```

---


## Section 5 — Final polish (Tasks 16–18)

Repository hygiene, end-to-end validation across all six pages, and the GitHub Pages configuration to deploy the site.

---

### Task 16: Update `CLAUDE.md` and `.gitignore`

**Files:**
- Modify: `CLAUDE.md`
- Modify: `.gitignore`

The current `CLAUDE.md` claims a "single-page" structure; the design doc supersedes that. Bring it up to date and add path conventions so future agents do not accidentally introduce absolute paths that break the GitHub Pages subpath. Also make sure `.gitignore` keeps the uv-managed virtualenv out of git but lets the generated `images/web/` content stay tracked.

- [ ] **Step 1: Read the current CLAUDE.md**

Run: `cat CLAUDE.md`

Expected: prints the current file. Note its existing tone and headings.

- [ ] **Step 2: Replace `CLAUDE.md` with the updated version**

Replace the entire contents of `CLAUDE.md` with:

```markdown
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
```

- [ ] **Step 3: Add `.gitignore` rules for the uv environment**

Read the current `.gitignore`:

Run: `cat .gitignore`

Then make sure these lines are present (append any that are missing):

```
# uv-managed virtualenv inside scripts/
scripts/.venv/

# Editor / OS scratch
.DS_Store
*.swp
.idea/
.vscode/

# Pytest cache
.pytest_cache/
```

If the file already contains all of these lines, leave it as-is.

- [ ] **Step 4: Verify generated images are NOT ignored**

Run: `git check-ignore images/web/_manifest.json && echo "WRONG" || echo "OK"`

Expected: prints `OK`. (We want `images/web/` tracked, since GitHub Pages needs to serve it.)

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md .gitignore
git commit -m "Update CLAUDE.md for multi-page structure; refine .gitignore"
```

---

### Task 17: Full-site validation pass

**Files:**
- (none — verification only)

A single end-to-end sweep across every page, catching regressions from the per-page tasks.

- [ ] **Step 1: HTML validate every page**

Run:

```bash
for f in index.html about.html projects/*.html; do
  echo "=== $f ==="
  tidy -q -e "$f" 2>&1 | grep -E '(Error|Warning):' || echo "(clean)"
done
```

Expected: every page reports `(clean)`. Any `Error:` line means the page has invalid HTML — fix before continuing.

- [ ] **Step 2: Verify no absolute paths into the site's own resources**

Run:

```bash
grep -RnE 'href="/|src="/' index.html about.html projects/ styles/ || echo "OK"
```

Expected: prints `OK`. Absolute paths break under a GitHub Pages subpath.

- [ ] **Step 3: Verify no Google Fonts request**

Run:

```bash
grep -RnE 'fonts.googleapis|fonts.gstatic' index.html about.html projects/ styles/ || echo "OK"
```

Expected: prints `OK`. Self-hosted only.

- [ ] **Step 4: Verify project-02/image-07 is nowhere referenced**

Run:

```bash
grep -RnE 'project-02/image-07|project-2/image-07' index.html about.html projects/ styles/ || echo "OK"
```

Expected: prints `OK`.

- [ ] **Step 5: Verify every `<img>` has `alt`**

Run:

```bash
python3 - <<'PY'
import re, sys, glob
bad = []
for path in glob.glob('index.html') + glob.glob('about.html') + glob.glob('projects/*.html'):
    text = open(path).read()
    for m in re.finditer(r'<img\b[^>]*>', text):
        tag = m.group(0)
        if 'alt=' not in tag:
            bad.append(f'{path}: {tag[:120]}')
if bad:
    print('MISSING ALT:')
    print('\n'.join(bad))
    sys.exit(1)
print('OK - every img has alt')
PY
```

Expected: prints `OK - every img has alt`.

- [ ] **Step 6: Verify every `<img>` has `width` and `height` (no remaining `W`/`H` placeholders)**

Run:

```bash
python3 - <<'PY'
import re, sys, glob
bad = []
for path in glob.glob('index.html') + glob.glob('about.html') + glob.glob('projects/*.html'):
    text = open(path).read()
    for m in re.finditer(r'<img\b[^>]*>', text):
        tag = m.group(0)
        if 'width=' not in tag or 'height=' not in tag:
            bad.append(f'{path}: missing width/height: {tag[:120]}')
        if re.search(r'width="W"|height="H"', tag):
            bad.append(f'{path}: placeholder left in: {tag[:120]}')
if bad:
    print('FAIL:')
    print('\n'.join(bad))
    sys.exit(1)
print('OK - every img has real width/height')
PY
```

Expected: prints `OK - every img has real width/height`. Any failures mean an engineer forgot to substitute the manifest values during a project task — open the listed file and fix.

- [ ] **Step 7: Verify the contact placeholders are still placeholders (so the user knows to replace them)**

Run:

```bash
grep -nE 'REPLACE-ME|\\+00 000 000 000' about.html
```

Expected: prints two lines (one for the email, one for the phone). The placeholder is intentional until Eleni provides the real values.

- [ ] **Step 8: Lighthouse audit on every page**

In Chrome DevTools, run a Lighthouse audit (Mobile, Accessibility category) for each of:
- `index.html`
- `about.html`
- `projects/01-xanthi-pavilion.html`
- `projects/02-tobacco-warehouse.html`
- `projects/03-therma-spa.html`
- `projects/04-historic-restoration.html`

Expected: every page scores **100** Accessibility, **0** contrast issues, **0** "image without alt" issues, **0** "low-contrast text" issues.

- [ ] **Step 9: CLS check on every page**

In Chrome DevTools → Performance → record a reload of each of the six pages.

Expected: every page reports CLS `< 0.01`.

- [ ] **Step 10: Page-weight check on the heaviest page**

Open `projects/02-tobacco-warehouse.html` in Chrome with DevTools → Network → Disable cache, then reload.

Expected: total transferred ≤ **3 MB** with lazy-loading active (images below the fold should not appear in the network log until you scroll).

- [ ] **Step 11: Print test (optional but recommended for an architecture portfolio)**

In Chrome, press Cmd/Ctrl-P on each page.

Expected: print preview is legible (text in black on white, drawings visible). If sticky-header or vertical-hairline pseudo-elements break print layout, add a `@media print { .site-header { position: static; } .hero::after { display: none; } }` block to `styles/base.css`. Otherwise leave as-is.

- [ ] **Step 12: Commit any fixes the validation pass surfaced**

If steps 1–11 produced no failures: there is nothing to commit. Skip.

If they did:

```bash
git add -A
git commit -m "Fix issues surfaced by full-site validation pass"
```

---

### Task 18: Configure GitHub Pages and deploy

**Files:**
- Create: `.github/workflows/pages.yml` (only if the repo's GitHub Pages setting is "GitHub Actions"; skip if using "Deploy from a branch")
- Create: `.nojekyll`

GitHub Pages serves static sites by default but can quietly skip directories whose names start with an underscore. We add `.nojekyll` to prevent that and (optionally) a Pages-deploy workflow.

- [ ] **Step 1: Add `.nojekyll`**

Run: `touch .nojekyll`

Expected: file exists at the repo root.

- [ ] **Step 2: Decide deployment mode**

Open the GitHub repo settings page → Pages. Two options:

A. **Deploy from a branch** — Pages serves from the branch root (e.g., `main`). No workflow needed; simply pushing to `main` redeploys. Skip step 3.

B. **GitHub Actions** — Pages is built and deployed by a workflow. Continue to step 3.

- [ ] **Step 3 (only if option B): Create the deployment workflow**

Create `.github/workflows/pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: .
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 4: Commit**

```bash
git add .nojekyll .github/workflows/pages.yml 2>/dev/null
git add .nojekyll
git commit -m "Configure GitHub Pages deployment"
```

(If you skipped the workflow file, only `.nojekyll` is staged — that is fine.)

- [ ] **Step 5: Push and verify deployment**

Run:

```bash
git push origin HEAD
```

Then watch the GitHub Actions tab (option B) or the "Pages" status (option A) until the deployment completes.

Expected: the live site loads at the URL shown in the GitHub Pages settings (typically `https://<user>.github.io/<repo>/`). Open every page and verify:
- All fonts loaded (no FOUT — text appears in Jost, not in fallback geometric sans).
- All images visible at every breakpoint.
- Header nav works between pages.
- `about.html#contact` scrolls to the Contact block.

- [ ] **Step 6: Final smoke test from a clean checkout**

Run:

```bash
cd /tmp
git clone <this-repo-url> portfolio-clean
cd portfolio-clean
xdg-open index.html
```

Expected: opens `index.html` directly via `file://` — every link, image, font, and stylesheet must still load. Walking through Work → each project → About → back to home must work without a server.

This double-checks the relative-paths convention. Any 404 in the browser console here means an absolute path snuck in somewhere; re-run Task 17 step 2 to find it.

- [ ] **Step 7: Tag the release (optional)**

If the deploy looks good and Eleni has confirmed the site:

```bash
git tag v1.0
git push origin v1.0
```

---

## Self-review checklist

Before considering the plan complete, the implementer should confirm:

- [ ] All eight acceptance criteria in spec §9 are satisfied:
  1. `file://` open of `index.html` renders correctly with all assets — Task 17 step 6 + Task 18 step 6.
  2. Header nav navigates correctly across all six pages — Task 17 step 8 (Lighthouse navigation audit) + manual smoke.
  3. Each project page displays every image in the documented order with captions; `project-02/image-07.jpeg` not present anywhere — Tasks 12–15 + Task 17 step 4.
  4. About page has all CV content with placeholders for email/phone — Task 11 + Task 17 step 7.
  5. Lighthouse Accessibility 100, AAA body, AA-large accent — Task 17 step 8.
  6. CLS ≈ 0 — Task 17 step 9.
  7. Heaviest page < 3 MB initial load — Task 17 step 10.
  8. Renders cleanly at 360px / 768px / 1440px — verified per page in Tasks 10–15 + Task 17.

- [ ] All five files in the "Modified" / "Created" file plan exist with the documented responsibilities.
- [ ] `images/web/` is committed and contains 60 sources × 3 variants = 180 JPEGs plus `_manifest.json`.
- [ ] No JavaScript was added (the site has no `<script>` tags).

