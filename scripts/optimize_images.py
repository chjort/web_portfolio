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
