```text
   ┌──────────────────────────────────────────────────┐
   │  c o d e c h u — f s                             │
   │   .                                              │
   │   ├── atomic_write()    safe.tmp -> fsync -> mv  │
   │   ├── move_to_trash()   ~/.local/share/Trash/    │
   │   ├── walk()            cancellable + loop-safe  │
   │   └── mountpoint()      /proc/mounts aware       │
   └──────────────────────────────────────────────────┘
```

[![PyPI](https://img.shields.io/pypi/v/codechu-fs.svg)](https://pypi.org/project/codechu-fs/)
[![Python](https://img.shields.io/pypi/pyversions/codechu-fs.svg)](https://pypi.org/project/codechu-fs/)
[![CI](https://github.com/codechu/fs-py/actions/workflows/ci.yml/badge.svg)](https://github.com/codechu/fs-py/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> *Filesystem primitives for tools that must not lose data.*

# codechu-fs

Stdlib-only filesystem helpers that turn the easy-to-get-wrong cases
(half-written config, swallowed walk errors, runaway recursive size)
into one-liners. Atomic writes that fsync. Walks that cancel. Trash
that follows the freedesktop spec. Mountpoints that read
`/proc/mounts` properly.

## Install

```bash
pip install codechu-fs
```

Python 3.10+. Zero third-party dependencies.

## Quick example

```python
from pathlib import Path
from threading import Event
from codechu_fs import atomic_write, move_to_trash, walk, recursive_size, temp_dir

# Crash-safe: tempfile in same dir → fsync → rename. Permissions preserved.
atomic_write("/etc/myapp/config.json", b'{"k":1}\n')

# XDG Trash Specification compliant — recoverable from the file manager.
trashed = move_to_trash("/tmp/junk.log")

# Cancellable walk — GUI cancel buttons actually stop the scan.
cancel = Event()
for dirpath, dirs, files in walk("/var/log", cancel=cancel):
    if user_clicked_cancel():
        cancel.set()

# Cancellable size, mountpoint, scratch dir
print(recursive_size(Path.home() / "Downloads"))
with temp_dir(prefix="myapp-") as scratch:
    (scratch / "work.bin").write_bytes(b"…")
```

## What you get

- **`atomic_write`** — tempfile in the same dir, `fsync`, then
  `rename`. Preserves existing permissions. Bytes or text.
- **`move_to_trash`** — freedesktop XDG Trash Specification
  compliant. Honors `XDG_DATA_HOME`, writes `.trashinfo`, resolves
  name collisions.
- **`walk`** — `os.walk` plus a `cancel` Event, an `on_error`
  callback (no silent swallow), and symlink-loop detection.
- **`recursive_size`** — sum of bytes under a directory,
  cancellable, skips unreadable files.
- **`mountpoint`** — the mount that contains a path, parsed from
  `/proc/mounts` on Linux with a `st_dev` fallback elsewhere.
- **`is_safe_path`** — path-traversal guard for user-supplied
  inputs.
- **`temp_dir`** — context-managed temp directory, auto-removed.

## Read more

- [API reference](docs/API.md) — every public symbol with full
  signatures and edge-case tables.
- [Recipes](docs/RECIPES.md) — atomic save with backup, cancellable
  scan with progress, post-crash trash recovery, mount-aware free
  space, traversal sandboxing.
- [Changelog](CHANGELOG.md)

## Family

| Library | Purpose |
|---------|---------|
| [codechu-xdg](https://pypi.org/project/codechu-xdg/) | XDG Base Directory helpers, vendor-namespaced |
| [codechu-config](https://pypi.org/project/codechu-config/) | Schema-driven config — atomic save, migrations |
| [codechu-fmt](https://pypi.org/project/codechu-fmt/) | Human-readable sizes, durations, rates |
| [codechu-treeviz](https://pypi.org/project/codechu-treeviz/) | Treemap + sunburst layouts |
| [codechu-events](https://pypi.org/project/codechu-events/) | Thread-safe multi-channel pub/sub bus |

Full ecosystem: [github.com/codechu](https://github.com/codechu).

## Credits

- XDG Trash Specification by freedesktop.org.
- Atomic write pattern follows POSIX `rename(2)` guarantees.

## License

MIT — see [LICENSE](LICENSE).

Part of [Codechu](https://github.com/codechu).
