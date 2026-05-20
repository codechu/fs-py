from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote

import pytest

from codechu_fs import move_to_trash


def _env_for(tmp_path: Path) -> dict[str, str]:
    return {"XDG_DATA_HOME": str(tmp_path / "share"), "HOME": str(tmp_path)}


def test_trash_basic(tmp_path: Path) -> None:
    env = _env_for(tmp_path)
    src = tmp_path / "junk.txt"
    src.write_text("bye", encoding="utf-8")
    dest = move_to_trash(src, env=env)
    assert dest.exists()
    assert dest.read_text(encoding="utf-8") == "bye"
    assert not src.exists()
    info = dest.parent.parent / "info" / f"{dest.name}.trashinfo"
    assert info.exists()
    text = info.read_text(encoding="utf-8")
    assert text.startswith("[Trash Info]\n")
    assert "DeletionDate=" in text
    # Path is URL-encoded.
    path_line = next(ln for ln in text.splitlines() if ln.startswith("Path="))
    assert unquote(path_line[len("Path=") :]) == str(src.resolve())


def test_trash_collision(tmp_path: Path) -> None:
    env = _env_for(tmp_path)
    for i in range(3):
        f = tmp_path / "dup.txt"
        f.write_text(f"v{i}", encoding="utf-8")
        move_to_trash(f, env=env)
    files_dir = Path(env["XDG_DATA_HOME"]) / "Trash" / "files"
    names = sorted(p.name for p in files_dir.iterdir())
    assert names == ["dup.1.txt", "dup.2.txt", "dup.txt"]


def test_trash_directory(tmp_path: Path) -> None:
    env = _env_for(tmp_path)
    d = tmp_path / "a-dir"
    d.mkdir()
    (d / "inside.txt").write_text("hi", encoding="utf-8")
    dest = move_to_trash(d, env=env)
    assert dest.is_dir()
    assert (dest / "inside.txt").read_text(encoding="utf-8") == "hi"


def test_trash_missing_file(tmp_path: Path) -> None:
    env = _env_for(tmp_path)
    with pytest.raises(FileNotFoundError):
        move_to_trash(tmp_path / "nope", env=env)


def test_trash_uses_xdg_data_home_default(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    src = tmp_path / "x.txt"
    src.write_text("z", encoding="utf-8")
    dest = move_to_trash(src)
    assert str(dest).startswith(str(tmp_path / ".local" / "share" / "Trash" / "files"))


def test_trash_no_home(tmp_path: Path) -> None:
    src = tmp_path / "anything"
    src.write_text("x", encoding="utf-8")
    with pytest.raises(RuntimeError):
        move_to_trash(src, env={})
