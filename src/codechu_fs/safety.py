"""Path-traversal defense."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union

PathLike = Union[str, os.PathLike]


def is_safe_path(path: PathLike, base: PathLike) -> bool:
    """Return True iff ``path`` resolves to a location under ``base``.

    Both arguments are resolved with ``Path.resolve()`` so symlinks and
    ``..`` segments are normalised. Useful before extracting archives or
    serving user-supplied filenames.

    Does not require either path to exist on disk.
    """
    try:
        resolved = Path(path).resolve()
        anchor = Path(base).resolve()
    except (OSError, RuntimeError):
        return False
    try:
        resolved.relative_to(anchor)
    except ValueError:
        return False
    return True
