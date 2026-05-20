# Changelog

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) + [SemVer](https://semver.org/).

## [Unreleased]

## [0.1.0] — 2026-05-20

### Added
- `atomic_write(path, data, *, mode=0o644, encoding=None)` — durable
  write via tempfile-in-same-dir + `fsync` + `rename`. Preserves
  existing file permissions; accepts `bytes` or (with `encoding`) `str`.
- `move_to_trash(path, *, env=None)` — freedesktop XDG Trash
  Specification compliant move into `$XDG_DATA_HOME/Trash/`. Writes
  `.trashinfo` with `DeletionDate` and resolves name collisions by
  numeric suffix. Returns the trashed `Path`.
- `walk(root, *, follow_symlinks=False, cancel=None, on_error=None)` —
  generator like `os.walk`, but detects symlink loops, accepts a
  `threading.Event` for cooperative cancellation, and reports
  `OSError` via `on_error` instead of swallowing them.
- `recursive_size(path, *, cancel=None, follow_symlinks=False)` — sum
  of file sizes under a path; cancellable.
- `mountpoint(path)` — `Path` of the mountpoint containing `path`,
  reading `/proc/mounts` on Linux and falling back to a `st_dev` walk
  elsewhere.
- `is_safe_path(path, base)` — defensive path-traversal check; True
  iff `path.resolve()` is contained under `base.resolve()`.
- `temp_dir(prefix="codechu-", parent=None)` — context manager yielding
  a `Path` to a fresh temp directory, auto-removed on exit.
