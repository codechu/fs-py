"""XDG Trash Specification implementation.

See: https://specifications.freedesktop.org/trash-spec/trashspec-1.0.html
"""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Mapping, Union
from urllib.parse import quote

PathLike = Union[str, os.PathLike]


def _xdg_data_home(env: Mapping[str, str]) -> Path:
    raw = env.get("XDG_DATA_HOME")
    if raw:
        return Path(raw)
    home = env.get("HOME")
    if not home:
        raise RuntimeError("cannot locate XDG_DATA_HOME (no HOME env var)")
    return Path(home) / ".local" / "share"


def _resolve_name(directory: Path, name: str) -> str:
    """Pick a non-colliding filename inside ``directory``."""
    candidate = name
    counter = 1
    stem = Path(name).stem
    suffix = "".join(Path(name).suffixes)
    while (directory / candidate).exists() or (
        directory.parent / "info" / f"{candidate}.trashinfo"
    ).exists():
        candidate = f"{stem}.{counter}{suffix}"
        counter += 1
        if counter > 9999:
            raise RuntimeError(f"too many trash collisions for {name!r}")
    return candidate


def _format_trashinfo(original_path: Path, deletion_time: datetime) -> str:
    # XDG spec: Path must be URL-encoded, but '/' is preserved.
    encoded = quote(str(original_path), safe="/")
    iso = deletion_time.strftime("%Y-%m-%dT%H:%M:%S")
    return f"[Trash Info]\nPath={encoded}\nDeletionDate={iso}\n"


def move_to_trash(path: PathLike, *, env: Mapping[str, str] | None = None) -> Path:
    """Move ``path`` into the user's XDG trash.

    Follows the freedesktop.org Trash Specification 1.0:

    - Files are moved into ``$XDG_DATA_HOME/Trash/files/``.
    - A matching ``.trashinfo`` is written to ``$XDG_DATA_HOME/Trash/info/``
      containing the URL-encoded original ``Path`` and an ISO-8601
      ``DeletionDate``.
    - Name collisions are resolved by appending ``.N`` before the suffix.

    ``env`` defaults to ``os.environ``.

    Returns the final ``Path`` inside the trash ``files/`` directory.
    """
    src = Path(path)
    if not src.exists() and not src.is_symlink():
        raise FileNotFoundError(src)

    environ = dict(os.environ) if env is None else dict(env)
    trash_root = _xdg_data_home(environ) / "Trash"
    files_dir = trash_root / "files"
    info_dir = trash_root / "info"
    files_dir.mkdir(parents=True, exist_ok=True)
    info_dir.mkdir(parents=True, exist_ok=True)

    original_abs = src.resolve() if src.is_symlink() is False else src.absolute()
    final_name = _resolve_name(files_dir, src.name)
    info_path = info_dir / f"{final_name}.trashinfo"
    target = files_dir / final_name

    info_path.write_text(
        _format_trashinfo(original_abs, datetime.now()),
        encoding="utf-8",
    )
    try:
        shutil.move(str(src), str(target))
    except Exception:
        # Roll back the info file if the move failed.
        try:
            info_path.unlink()
        except FileNotFoundError:
            pass
        raise
    return target
