# CLAUDE.md — codechu-fs

Bootstrap per `codechu-org/ai/AGENTS.md` §0 before any work. Prefer
the local clone at `$org_home/codechu-org/ai/AGENTS.md` (if
`~/.config/codechu/config.toml` has `org_home` set); otherwise
WebFetch the public raw URL
<https://raw.githubusercontent.com/codechu/codechu-org/main/ai/AGENTS.md>.
This file lists only product-local overrides.

## Product-local notes

- Pure stdlib filesystem primitives. **No** external runtime dependencies.
- Public API (re-exported from `codechu_fs`): `atomic_write`,
  `move_to_trash`, `walk`, `recursive_size`, `mountpoint`,
  `is_safe_path`, `temp_dir`. Submodule internals are not API.
- `move_to_trash` follows the freedesktop.org XDG Trash Specification;
  changing the on-disk layout of `.trashinfo` is a breaking change.
- `walk` must never swallow `OSError` silently — either yield it via
  `on_error` or let it propagate.
- Never call `os.fsync` on a missing file descriptor; `atomic_write`
  must `fsync` before `rename`, and the rename target must be on the
  same filesystem as the tempfile.
- Coverage target: ≥85 % (mount/trash branches are platform-gated).

## Discipline reminders (org rules apply)

- Conventional Commits, no AI signature.
- No `--no-verify`, no force push, no unapproved publish.
- See `codechu-org/ai/AGENTS.md` for the full list.
