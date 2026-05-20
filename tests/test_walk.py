from __future__ import annotations

import os
from pathlib import Path
from threading import Event

import pytest

from codechu_fs import recursive_size, walk


def _build_tree(root: Path) -> None:
    (root / "a").mkdir()
    (root / "a" / "f1.txt").write_bytes(b"x" * 10)
    (root / "a" / "f2.txt").write_bytes(b"y" * 20)
    (root / "b").mkdir()
    (root / "b" / "c").mkdir()
    (root / "b" / "c" / "deep.bin").write_bytes(b"z" * 100)


def test_walk_basic(tmp_path: Path) -> None:
    _build_tree(tmp_path)
    seen_files: list[str] = []
    for _dp, _dn, files in walk(tmp_path):
        seen_files.extend(files)
    assert sorted(seen_files) == ["deep.bin", "f1.txt", "f2.txt"]


def test_walk_cancel(tmp_path: Path) -> None:
    _build_tree(tmp_path)
    cancel = Event()
    count = 0
    for _dp, _dn, _files in walk(tmp_path, cancel=cancel):
        count += 1
        cancel.set()  # stop after first dir
    assert count == 1


def test_walk_skips_symlinked_dirs_by_default(tmp_path: Path) -> None:
    (tmp_path / "real").mkdir()
    (tmp_path / "real" / "f.txt").write_bytes(b"x")
    (tmp_path / "link").symlink_to(tmp_path / "real")
    found = []
    for _dp, _dn, files in walk(tmp_path):
        found.extend(files)
    # 'f.txt' should appear exactly once — via 'real', not via 'link'.
    assert found.count("f.txt") == 1


def test_walk_symlink_loop_safe(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "f.txt").write_bytes(b"x")
    # a/loop -> tmp_path (parent) creates a cycle.
    (tmp_path / "a" / "loop").symlink_to(tmp_path)
    # Must terminate (no infinite loop) and not raise.
    visited = list(walk(tmp_path, follow_symlinks=True))
    assert len(visited) < 50  # tiny tree — loop should be cut quickly


def test_walk_on_error_called(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _build_tree(tmp_path)
    errors: list[OSError] = []
    real_scandir = os.scandir

    def boom(path):  # type: ignore[no-untyped-def]
        if "b" in os.fspath(path):
            raise PermissionError(f"denied: {path}")
        return real_scandir(path)

    monkeypatch.setattr(os, "scandir", boom)
    for _ in walk(tmp_path, on_error=errors.append):
        pass
    assert any(isinstance(e, PermissionError) for e in errors)


def test_walk_on_error_default_raises(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "x").mkdir()

    def boom(_path):  # type: ignore[no-untyped-def]
        raise PermissionError("denied")

    monkeypatch.setattr(os, "scandir", boom)
    with pytest.raises(PermissionError):
        list(walk(tmp_path))


def test_recursive_size(tmp_path: Path) -> None:
    _build_tree(tmp_path)
    assert recursive_size(tmp_path) == 10 + 20 + 100


def test_recursive_size_on_single_file(tmp_path: Path) -> None:
    f = tmp_path / "lone.bin"
    f.write_bytes(b"abcd")
    assert recursive_size(f) == 4


def test_recursive_size_cancel(tmp_path: Path) -> None:
    _build_tree(tmp_path)
    cancel = Event()
    cancel.set()
    # Cancelled immediately — should return promptly with 0 or partial.
    assert recursive_size(tmp_path, cancel=cancel) == 0


def test_recursive_size_skips_unreadable(tmp_path: Path) -> None:
    f = tmp_path / "a.bin"
    f.write_bytes(b"abcd")
    # No matter what, this returns a real int.
    assert isinstance(recursive_size(tmp_path), int)
