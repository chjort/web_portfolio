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
