# API Reference — codechu-fs 0.1.0

Complete reference for every public symbol re-exported from the
`codechu_fs` package.

The package exposes seven functions plus a version string:

| Symbol                                | Kind     | Module                |
| ------------------------------------- | -------- | --------------------- |
| [`__version__`](#__version__)         | `str`    | `codechu_fs`          |
| [`atomic_write`](#atomic_write)       | function | `codechu_fs.atomic`   |
| [`is_safe_path`](#is_safe_path)       | function | `codechu_fs.safety`   |
| [`mountpoint`](#mountpoint)           | function | `codechu_fs.mount`    |
| [`move_to_trash`](#move_to_trash)     | function | `codechu_fs.trash`    |
| [`recursive_size`](#recursive_size)   | function | `codechu_fs.walk`     |
| [`temp_dir`](#temp_dir)               | function | `codechu_fs.tempdir`  |
| [`walk`](#walk)                       | function | `codechu_fs.walk`     |

All functions depend only on the Python standard library.

---

## `__version__`

```python
__version__: str = "0.1.0"
```

Semantic-version string of the installed package.

---

## `atomic_write`

```python
def atomic_write(
    path: str | os.PathLike,
    data: bytes | str,
    *,
    mode: int = 0o644,
    encoding: str | None = None,
) -> pathlib.Path: ...
```

Atomically write `data` to `path`. Internally:

1. Creates a tempfile in the same directory as `path`.
2. Writes the payload, flushes, and `fsync`s the file descriptor.
3. `chmod`s the tempfile to either the preserved existing mode (if
   `path` already existed) or the supplied `mode` (for new files).
4. `os.replace`s the tempfile over `path` — this is atomic on POSIX
   when both paths live on the same filesystem.

If any step fails, the tempfile is best-effort removed so callers do
not leak `.config.json.tmp` debris.

`data` must be `bytes`, `bytearray`, `memoryview`, or `str`. `str`
input requires the `encoding` keyword argument (e.g. `"utf-8"`).

Returns the resolved `Path` to the final file.

Raises:

- `FileNotFoundError` — the parent directory does not exist.
- `TypeError` — `data` is `str` without `encoding=`, or some other
  type entirely.

---

## `move_to_trash`

```python
def move_to_trash(
    path: str | os.PathLike,
    *,
    env: Mapping[str, str] | None = None,
) -> pathlib.Path: ...
```

Move `path` into the user's XDG trash, conforming to the
[freedesktop.org Trash Specification 1.0](
https://specifications.freedesktop.org/trash-spec/trashspec-1.0.html).

- Files land in `$XDG_DATA_HOME/Trash/files/`.
- A sibling `$XDG_DATA_HOME/Trash/info/<name>.trashinfo` records the
  URL-encoded original `Path` and an ISO-8601 `DeletionDate`.
- Name collisions are resolved by inserting `.1`, `.2`, … before the
  suffix. The first 9999 collisions are tolerated.

If the move itself fails, the `.trashinfo` is rolled back so the trash
remains consistent.

`env` defaults to a snapshot of `os.environ`. Pass an explicit mapping
for tests or non-interactive contexts.

Returns the destination `Path` inside `Trash/files/`.

Raises:

- `FileNotFoundError` — `path` does not exist.
- `RuntimeError` — neither `XDG_DATA_HOME` nor `HOME` is set in `env`.

This implementation only handles the **home trash**; per-volume trash
directories (`$topdir/.Trash-$uid`) for files on other mountpoints are
not yet implemented and will land in a later release.

---

## `walk`

```python
def walk(
    root: str | os.PathLike,
    *,
    follow_symlinks: bool = False,
    cancel: threading.Event | None = None,
    on_error: Callable[[OSError], None] | None = None,
) -> Iterator[tuple[str, list[str], list[str]]]: ...
```

Generator with the same `(dirpath, dirnames, filenames)` shape as
`os.walk`, plus three improvements:

- **Cancellable.** If `cancel.is_set()` becomes True between yields,
  iteration ends. Useful in GUI apps where a long scan must be
  abortable.
- **Loop-safe.** With `follow_symlinks=True`, the walker remembers
  every `(st_dev, st_ino)` it has visited and skips revisits, so
  symlinks back to ancestors cannot wedge the process.
- **Error-routed.** Errors from `os.scandir` and `entry.is_dir` are
  forwarded to `on_error(exc)` instead of silently dropped. If
  `on_error` is `None`, the error is raised.

`dirnames` lists *directory* entries (regular dirs always; symlinks to
dirs only when `follow_symlinks=True`); everything else goes in
`filenames`.

---

## `recursive_size`

```python
def recursive_size(
    path: str | os.PathLike,
    *,
    cancel: threading.Event | None = None,
    follow_symlinks: bool = False,
) -> int: ...
```

Sum of `st_size` for every regular file under `path`. Unreadable or
disappearing files are silently skipped (returning the partial total
is more useful than crashing a long scan). Honors `cancel` between
directories.

If `path` is itself a file, returns its size directly; if it does not
exist, returns `0`.

---

## `mountpoint`

```python
def mountpoint(path: str | os.PathLike) -> pathlib.Path: ...
```

Return the `Path` of the filesystem mountpoint that contains `path`.

On Linux this parses `/proc/mounts` (decoding the standard `\040`,
`\011`, `\012`, `\134` octal escapes for space/tab/newline/backslash)
and picks the longest mountpoint that is an ancestor of the resolved
`path`. If `/proc/mounts` is unreadable (or empty), the function walks
parents and watches for `st_dev` changes, matching the semantics of
`os.path.ismount`.

Always returns *some* `Path` — never raises for missing files.

---

## `is_safe_path`

```python
def is_safe_path(path: str | os.PathLike, base: str | os.PathLike) -> bool: ...
```

Return True if and only if `Path(path).resolve()` is contained under
`Path(base).resolve()`. Use this before opening, extracting, or
serving user-supplied filenames to defeat `../`-style traversal and
symlink escapes. Neither argument needs to exist.

---

## `temp_dir`

```python
@contextmanager
def temp_dir(
    prefix: str = "codechu-",
    parent: str | os.PathLike | None = None,
) -> Iterator[pathlib.Path]: ...
```

Context manager that creates a fresh temp directory and yields its
`Path`. The directory (and any contents) is recursively removed on
exit; if it was already removed, no error is raised. `parent`
overrides the system default (`$TMPDIR` / `/tmp`).
