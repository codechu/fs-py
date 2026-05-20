"""Atomic file writes — tempfile in same dir, fsync, rename."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike]


def atomic_write(
    path: PathLike,
    data: Union[bytes, str],
    *,
    mode: int = 0o644,
    encoding: str | None = None,
) -> Path:
    """Atomically write ``data`` to ``path``.

    Writes to a tempfile in the same directory (so ``rename`` is atomic on
    the same filesystem), fsyncs, then renames over ``path``.

    If ``path`` already exists its mode is preserved (the ``mode`` argument
    only applies when the file is new).

    ``data`` may be ``bytes`` or ``str``. ``str`` requires ``encoding`` to
    be set (e.g. ``"utf-8"``).

    Returns the final ``Path``.
    """
    target = Path(path)
    parent = target.parent
    if not parent.exists():
        raise FileNotFoundError(f"parent directory does not exist: {parent}")

    if isinstance(data, str):
        if encoding is None:
            raise TypeError("str data requires encoding=")
        payload = data.encode(encoding)
    elif isinstance(data, (bytes, bytearray, memoryview)):
        payload = bytes(data)
    else:
        raise TypeError(f"data must be bytes or str, got {type(data).__name__}")

    # Preserve existing perms if the target exists.
    existing_mode: int | None = None
    try:
        existing_mode = target.stat().st_mode & 0o7777
    except FileNotFoundError:
        existing_mode = None

    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=str(parent),
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        final_mode = existing_mode if existing_mode is not None else mode
        os.chmod(tmp_path, final_mode)
        os.replace(tmp_path, target)
    except Exception:
        # Best-effort cleanup on failure.
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise
    return target
