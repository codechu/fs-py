"""Cancellable, loop-safe filesystem walk + recursive size."""

from __future__ import annotations

import os
from pathlib import Path
from threading import Event
from typing import Callable, Iterator, Union

PathLike = Union[str, os.PathLike]


def walk(
    root: PathLike,
    *,
    follow_symlinks: bool = False,
    cancel: Event | None = None,
    on_error: Callable[[OSError], None] | None = None,
) -> Iterator[tuple[str, list[str], list[str]]]:
    """Like ``os.walk`` but cancellable, loop-safe, and error-routed.

    - ``follow_symlinks``: if True, follows directory symlinks but tracks
      visited ``(st_dev, st_ino)`` pairs to break loops.
    - ``cancel``: if set (``Event.is_set()``), the generator stops yielding
      and returns.
    - ``on_error``: callable receiving ``OSError`` instances raised by
      ``os.scandir`` on inaccessible directories. If ``None``, errors are
      raised.

    Yields ``(dirpath_str, dirnames, filenames)`` tuples top-down.
    """
    root_path = os.fspath(root)
    visited: set[tuple[int, int]] = set()

    def _step(current: str) -> Iterator[tuple[str, list[str], list[str]]]:
        if cancel is not None and cancel.is_set():
            return
        dirnames: list[str] = []
        filenames: list[str] = []
        try:
            with os.scandir(current) as it:
                entries = list(it)
        except OSError as exc:
            if on_error is not None:
                on_error(exc)
                return
            raise
        for entry in entries:
            try:
                is_dir = entry.is_dir(follow_symlinks=follow_symlinks)
            except OSError as exc:
                if on_error is not None:
                    on_error(exc)
                    continue
                raise
            if is_dir:
                dirnames.append(entry.name)
            else:
                filenames.append(entry.name)
        yield current, dirnames, filenames
        for name in list(dirnames):
            if cancel is not None and cancel.is_set():
                return
            child = os.path.join(current, name)
            if follow_symlinks:
                try:
                    st = os.stat(child)
                except OSError as exc:
                    if on_error is not None:
                        on_error(exc)
                        continue
                    raise
                key = (st.st_dev, st.st_ino)
                if key in visited:
                    continue
                visited.add(key)
            else:
                # Skip symlinked dirs entirely if not following.
                if os.path.islink(child):
                    continue
            yield from _step(child)

    # Seed visited set with root so following symlinks back to root halts.
    if follow_symlinks:
        try:
            st = os.stat(root_path)
            visited.add((st.st_dev, st.st_ino))
        except OSError as exc:
            if on_error is not None:
                on_error(exc)
                return
            raise

    yield from _step(root_path)


def recursive_size(
    path: PathLike,
    *,
    cancel: Event | None = None,
    follow_symlinks: bool = False,
) -> int:
    """Total size in bytes of all regular files under ``path``.

    Honors ``cancel`` (returns the partial total reached so far) and
    silently skips files that disappear or become unreadable mid-walk.
    """
    total = 0
    path_obj = Path(path)
    if path_obj.is_file():
        try:
            return path_obj.stat().st_size
        except OSError:
            return 0

    def _swallow(_exc: OSError) -> None:
        pass

    for dirpath, _dirnames, filenames in walk(
        path_obj,
        follow_symlinks=follow_symlinks,
        cancel=cancel,
        on_error=_swallow,
    ):
        if cancel is not None and cancel.is_set():
            break
        for name in filenames:
            full = os.path.join(dirpath, name)
            try:
                total += os.stat(full, follow_symlinks=follow_symlinks).st_size
            except OSError:
                continue
    return total
