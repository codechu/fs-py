# Recipes

Five idiomatic patterns for using `codechu-fs` in real code. Each
recipe is a self-contained snippet — copy, paste, adapt.

## 1. Atomically update a JSON config

You want to update an app config in `~/.config/myapp/config.json`
without ever leaving a half-written file on disk — even if the kernel
panics mid-write.

```python
import json
from pathlib import Path
from codechu_fs import atomic_write

config_path = Path.home() / ".config" / "myapp" / "config.json"
config_path.parent.mkdir(parents=True, exist_ok=True)

# Load -> mutate -> atomic write.
data = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
data["theme"] = "dark"

atomic_write(config_path, json.dumps(data, indent=2) + "\n", encoding="utf-8")
```

`atomic_write` `fsync`s before renaming, so a crash either leaves the
*old* file fully intact or the *new* file fully intact — never a torn
mix of the two.

## 2. Send a file to the desktop trash instead of `unlink`

Destructive UIs should send items to the trash so the user can recover
them from their file manager.

```python
from codechu_fs import move_to_trash

dest = move_to_trash("/tmp/old-report.pdf")
print(f"Recoverable at: {dest}")
```

The matching `.trashinfo` is written first; if the move fails the
`.trashinfo` is rolled back so the trash never contains a dangling
record.

## 3. Cancellable directory scan from a GUI

You're scanning `~/Downloads` to compute its size, but the user clicked
*Cancel*. The scan must stop within milliseconds.

```python
from pathlib import Path
from threading import Event, Thread
from codechu_fs import recursive_size

cancel = Event()
result: dict[str, int] = {}

def scan() -> None:
    result["bytes"] = recursive_size(Path.home() / "Downloads", cancel=cancel)

t = Thread(target=scan, daemon=True)
t.start()

# Later, when the user clicks Cancel:
cancel.set()
t.join()
print(result.get("bytes"))
```

`recursive_size` checks `cancel` between directories, so even
multi-million-file trees abort promptly.

## 4. Safe extraction of an untrusted upload path

Never trust a filename that came from outside your process. Validate
before opening or writing.

```python
from pathlib import Path
from codechu_fs import is_safe_path

UPLOADS = Path("/srv/uploads").resolve()

def save_upload(user_filename: str, blob: bytes) -> Path:
    target = UPLOADS / user_filename
    if not is_safe_path(target, UPLOADS):
        raise PermissionError(f"unsafe path: {user_filename}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(blob)
    return target

save_upload("../../etc/passwd", b"...")  # → PermissionError
save_upload("reports/q1.pdf", b"...")    # → /srv/uploads/reports/q1.pdf
```

## 5. Find the partition behind a path

For "free space on this disk" indicators or "is this on the same
volume?" checks, you need the mountpoint, not just the path.

```python
import shutil
from pathlib import Path
from codechu_fs import mountpoint

p = Path.home() / "video.mkv"
mp = mountpoint(p)
usage = shutil.disk_usage(mp)
print(f"{p} lives on {mp} — {usage.free / 1e9:.1f} GB free")
```

On Linux this reads `/proc/mounts` and picks the longest matching
mountpoint, so bind mounts and overlays resolve correctly.
