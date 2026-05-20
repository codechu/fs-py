"""Context-managed temporary directories."""

from __future__ import annotations

import contextlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterator, Union

PathLike = Union[str, os.PathLike]


@contextlib.contextmanager
def temp_dir(prefix: str = "codechu-", parent: PathLike | None = None) -> Iterator[Path]:
    """Yield a fresh temp directory ``Path``, recursively removed on exit.

    ``parent`` overrides the system default (``$TMPDIR`` / ``/tmp``).
    Cleanup is best-effort; an already-removed directory does not raise.
    """
    path = Path(tempfile.mkdtemp(prefix=prefix, dir=str(parent) if parent else None))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
