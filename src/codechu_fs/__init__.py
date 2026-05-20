"""codechu-fs — stdlib-only filesystem primitives.

Public API:

- atomic_write(path, data, *, mode=0o644, encoding=None)
- move_to_trash(path, *, env=None)
- walk(root, *, follow_symlinks=False, cancel=None, on_error=None)
- recursive_size(path, *, cancel=None, follow_symlinks=False)
- mountpoint(path)
- is_safe_path(path, base)
- temp_dir(prefix="codechu-", parent=None)
"""

from .atomic import atomic_write
from .mount import mountpoint
from .safety import is_safe_path
from .tempdir import temp_dir
from .trash import move_to_trash
from .walk import recursive_size, walk

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "atomic_write",
    "is_safe_path",
    "mountpoint",
    "move_to_trash",
    "recursive_size",
    "temp_dir",
    "walk",
]
