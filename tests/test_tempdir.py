from __future__ import annotations

from pathlib import Path

from codechu_fs import temp_dir


def test_temp_dir_yields_existing(tmp_path: Path) -> None:
    with temp_dir(parent=tmp_path) as d:
        assert d.is_dir()
        captured = d
    assert not captured.exists()


def test_temp_dir_cleans_with_contents(tmp_path: Path) -> None:
    with temp_dir(parent=tmp_path) as d:
        (d / "a.txt").write_text("x")
        (d / "sub").mkdir()
        (d / "sub" / "b.bin").write_bytes(b"y")
        captured = d
    assert not captured.exists()


def test_temp_dir_prefix(tmp_path: Path) -> None:
    with temp_dir(prefix="myapp-", parent=tmp_path) as d:
        assert d.name.startswith("myapp-")


def test_temp_dir_cleanup_ignores_missing(tmp_path: Path) -> None:
    # If the dir is removed before exit, the context manager must not raise.
    with temp_dir(parent=tmp_path) as d:
        import shutil

        shutil.rmtree(d)
    # exiting without error is the assertion
