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
