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

> *Filesystem primitives for tools that must not lose data.*

# codechu-fs

Stdlib-only filesystem helpers — atomic writes, XDG trash, cancellable
walks, mount discovery — extracted from the
[Disk Cleaner](https://github.com/codechu/disk-cleaner) toolchain.
Zero third-party dependencies. Python 3.10+.

## What it gives you

- **`atomic_write`** — tempfile in the same dir, `fsync`, then `rename`.
  Preserves existing permissions. Either bytes or text (with encoding).
- **`move_to_trash`** — freedesktop XDG Trash Specification compliant.
  Honors `XDG_DATA_HOME`, writes a `.trashinfo`, resolves name
  collisions.
- **`walk`** — `os.walk` with three things `os.walk` is missing: a
  `cancel` Event for cooperative shutdown, an `on_error` callback (no
  silent swallow), and symlink-loop detection when following links.
- **`recursive_size`** — sum of bytes under a directory, cancellable.
- **`mountpoint`** — the mount that contains a path, parsed from
  `/proc/mounts` on Linux with a `st_dev` fallback elsewhere.
- **`is_safe_path`** — path-traversal guard for user-supplied inputs.
- **`temp_dir`** — context-managed temp directory, auto-removed.

## Install

```bash
pip install codechu-fs
```

## Quick examples

```python
from pathlib import Path
from threading import Event
from codechu_fs import (
    atomic_write, move_to_trash, walk, recursive_size,
    mountpoint, is_safe_path, temp_dir,
)

# Durable write — never leaves a half-written file even if you crash mid-write.
atomic_write("/etc/myapp/config.json", b'{"k":1}\n')
atomic_write("notes.txt", "hello\n", encoding="utf-8")

# Send a file to the desktop trash (recoverable from the file manager).
trashed = move_to_trash("/tmp/junk.log")
print("now at:", trashed)

# Cancellable walk — stop instantly when the user clicks Cancel.
cancel = Event()
for dirpath, dirnames, filenames in walk("/var/log", cancel=cancel):
    if some_condition():
        cancel.set()

# Total size of a directory tree (skips unreadable files).
print(recursive_size(Path.home() / "Downloads"))

# What partition is this on?
print(mountpoint("/var/log/syslog"))   # → /var, or / on most systems

# Safe extraction of an untrusted filename.
if is_safe_path(user_input, base="/srv/uploads"):
    ...

# Scratch space that always cleans up.
with temp_dir(prefix="myapp-") as scratch:
    (scratch / "work.bin").write_bytes(b"...")
```

## Design

- **Pure stdlib.** Zero third-party dependencies. Seven small modules.
- **Defensive.** `walk` never swallows errors silently. `atomic_write`
  fsyncs before rename. `move_to_trash` rolls back its `.trashinfo` on
  failure.
- **Cancellable.** Every traversal accepts a `threading.Event`. Long
  scans on slow disks remain responsive in GUI apps.

## Tests

```bash
pip install -e ".[dev]"
pytest -q
```

## Documentation

- [API reference](docs/API.md) — every public symbol, signatures, edge cases
- [Recipes](docs/RECIPES.md) — five idiomatic patterns for CLIs and GUIs

## License

MIT — see [LICENSE](LICENSE).
