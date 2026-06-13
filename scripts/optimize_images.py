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
