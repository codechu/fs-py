# Contributing to codechu-fmt

Thanks for thinking about contributing. `codechu-fmt` is a tiny set
of stdlib-only human-readable formatters — durations, rates, byte
sizes. Patches that stay focused, well-tested, and dependency-free
are warmly received.

This library was originally extracted from [Disk Cleaner](https://github.com/codechu/disk-cleaner)
via [codechu/cli-py](https://github.com/codechu/cli-py), but is maintained
independently with its own release cadence.

## Development setup

```bash
git clone https://github.com/codechu/codechu-fmt-py.git
cd codechu-fmt-py
pip install -e ".[dev]"
pytest -q
ruff check src tests
```

## Workflow

- Branch names: `feature/<short>`, `fix/<short>`, `refactor/<short>`,
  `docs/<short>`, `test/<short>`.
- Commit messages: [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
- Open a PR using the template; describe the *why* in the body.
- One change per PR — keep diffs reviewable.

## Bug reports

A useful bug report includes:

- OS + Python version.
- The exact call you made and the string you got back.
- The string you expected.

## Tests

- `pytest -q` must pass; coverage stays at **≥90 %**.
- New feature → new test. Cover the edge cases: 0, sub-second /
  sub-byte, very large values, NaN, negatives.

## Public API discipline

The public surface is `format_duration`, `format_rate`, and
`format_size`. Output strings are part of the contract — changing
`'1m 30s'` → `'1min 30sec'` is a breaking change and ships in a major
version bump.

No external runtime dependencies. If you need one, the answer is
almost always "no, write it in stdlib".

## Style

- `ruff check` + `ruff format` clean.
- Type hints on public APIs (`from __future__ import annotations`).

## Security

If you find a security issue, see [SECURITY.md](SECURITY.md) — do not
open a public issue for it.

## Developer Certificate of Origin (DCO)

Every commit must be signed off with the [DCO](https://developercertificate.org/).
The sign-off certifies that you wrote the patch, or otherwise have the
right to submit it under the project's license. Add a line to your
commit message:

```
Signed-off-by: Your Name <you@example.com>
```

`git commit -s` does this automatically. PRs without sign-off will
be asked to amend before merge.

Contributions are accepted under the project's license (see
[LICENSE](LICENSE)).
