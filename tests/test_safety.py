from __future__ import annotations

from pathlib import Path

from codechu_fs import is_safe_path


def test_safe_path_inside(tmp_path: Path) -> None:
    inner = tmp_path / "sub" / "file"
    assert is_safe_path(inner, tmp_path)


def test_safe_path_equals_base(tmp_path: Path) -> None:
    assert is_safe_path(tmp_path, tmp_path)


def test_safe_path_traversal(tmp_path: Path) -> None:
    bad = tmp_path / ".." / ".." / "etc" / "passwd"
    assert not is_safe_path(bad, tmp_path)


def test_safe_path_unrelated(tmp_path: Path) -> None:
    assert not is_safe_path("/etc/passwd", tmp_path)


def test_safe_path_symlink_escapes_base(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside_target"
    outside.mkdir(exist_ok=True)
    try:
        link = tmp_path / "escape"
        link.symlink_to(outside)
        assert not is_safe_path(link, tmp_path)
    finally:
        if outside.exists():
            outside.rmdir()
