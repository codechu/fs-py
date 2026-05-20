from __future__ import annotations

from pathlib import Path

from codechu_fs import mountpoint


def test_mountpoint_returns_path() -> None:
    mp = mountpoint("/")
    assert isinstance(mp, Path)


def test_mountpoint_root_is_root() -> None:
    # On any sane Linux, '/' is a mountpoint of itself.
    assert mountpoint("/") == Path("/")


def test_mountpoint_for_tmp(tmp_path: Path) -> None:
    mp = mountpoint(tmp_path)
    # The mountpoint must be an ancestor (or equal).
    assert str(tmp_path.resolve()).startswith(str(mp))


def test_mountpoint_nonexistent_path(tmp_path: Path) -> None:
    # Even for a path that does not yet exist, resolve() gives a
    # synthetic absolute path; mountpoint() must still return some Path.
    mp = mountpoint(tmp_path / "does-not-exist" / "yet")
    assert isinstance(mp, Path)


def test_mountpoint_proc_decode(monkeypatch) -> None:
    # Force the fallback path by making /proc/mounts unreadable.
    from codechu_fs import mount as mount_mod

    monkeypatch.setattr(mount_mod, "_PROC_MOUNTS", "/no/such/file")
    assert isinstance(mountpoint("/"), Path)


def test_decode_mount_path_octal() -> None:
    from codechu_fs.mount import _decode_mount_path

    # space = \040, tab = \011
    assert _decode_mount_path(r"/mnt/with\040space") == "/mnt/with space"
    assert _decode_mount_path(r"/no/escapes") == "/no/escapes"
