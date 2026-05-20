"""Mountpoint discovery."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike]

_PROC_MOUNTS = "/proc/mounts"


def _read_proc_mounts() -> list[str]:
    try:
        with open(_PROC_MOUNTS, encoding="utf-8") as fh:
            return [line.split()[1] for line in fh if line.strip()]
    except OSError:
        return []


def _decode_mount_path(raw: str) -> str:
    # /proc/mounts encodes spaces / tabs / newlines / backslashes as octal.
    out: list[str] = []
    i = 0
    while i < len(raw):
        ch = raw[i]
        if ch == "\\" and i + 3 < len(raw) and raw[i + 1 : i + 4].isdigit():
            try:
                out.append(chr(int(raw[i + 1 : i + 4], 8)))
                i += 4
                continue
            except ValueError:
                pass
        out.append(ch)
        i += 1
    return "".join(out)


def mountpoint(path: PathLike) -> Path:
    """Return the mountpoint ``Path`` that contains ``path``.

    On Linux this reads ``/proc/mounts``; elsewhere (or if that file is
    unreadable) it walks parents and compares ``st_dev`` until it
    changes, matching ``os.path.ismount`` semantics.
    """
    resolved = Path(path).resolve()

    raw_mounts = _read_proc_mounts()
    if raw_mounts:
        decoded = [_decode_mount_path(m) for m in raw_mounts]
        # Pick the longest mountpoint that is an ancestor of resolved.
        best: str | None = None
        for mp in decoded:
            try:
                mp_path = Path(mp).resolve()
            except OSError:
                continue
            try:
                resolved.relative_to(mp_path)
            except ValueError:
                continue
            if best is None or len(str(mp_path)) > len(best):
                best = str(mp_path)
        if best is not None:
            return Path(best)

    # Fallback: climb until st_dev changes or we hit the root.
    try:
        cur = resolved
        cur_dev = cur.stat().st_dev
    except OSError:
        return Path("/")
    while cur != cur.parent:
        try:
            parent_dev = cur.parent.stat().st_dev
        except OSError:
            return cur
        if parent_dev != cur_dev:
            return cur
        cur = cur.parent
    return cur
