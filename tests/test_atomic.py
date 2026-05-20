"""Tests for atomic_write."""

from __future__ import annotations

import os
import threading
from pathlib import Path

import pytest

from codechu_fs import atomic_write


def test_write_bytes(tmp_path: Path) -> None:
    target = tmp_path / "data.bin"
    atomic_write(target, b"hello")
    assert target.read_bytes() == b"hello"


def test_write_str_requires_encoding(tmp_path: Path) -> None:
    target = tmp_path / "data.txt"
    with pytest.raises(TypeError):
        atomic_write(target, "hello")
    atomic_write(target, "hello", encoding="utf-8")
    assert target.read_text(encoding="utf-8") == "hello"


def test_overwrite_preserves_mode(tmp_path: Path) -> None:
    target = tmp_path / "secret"
    target.write_bytes(b"old")
    os.chmod(target, 0o600)
    atomic_write(target, b"new")
    assert target.read_bytes() == b"new"
    assert (target.stat().st_mode & 0o777) == 0o600


def test_new_file_uses_mode(tmp_path: Path) -> None:
    target = tmp_path / "fresh"
    atomic_write(target, b"x", mode=0o640)
    assert (target.stat().st_mode & 0o777) == 0o640


def test_rejects_bad_type(tmp_path: Path) -> None:
    with pytest.raises(TypeError):
        atomic_write(tmp_path / "f", 123)  # type: ignore[arg-type]


def test_parent_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        atomic_write(tmp_path / "nope" / "f", b"x")


def test_no_tmp_leftover(tmp_path: Path) -> None:
    target = tmp_path / "leftover.txt"
    atomic_write(target, b"ok")
    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".")]
    assert leftovers == []


def test_concurrent_writes_one_wins(tmp_path: Path) -> None:
    target = tmp_path / "race.bin"
    errors: list[Exception] = []

    def writer(payload: bytes) -> None:
        try:
            atomic_write(target, payload)
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(exc)

    threads = [
        threading.Thread(target=writer, args=(bytes([i] * 64),)) for i in range(10)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == []
    data = target.read_bytes()
    # The winning write must be intact — no partial / interleaved bytes.
    assert len(data) == 64
    assert len(set(data)) == 1
