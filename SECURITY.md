# Security policy

`codechu-fmt` is a pure-stdlib formatter library. Its public functions
take numbers and return strings — no I/O, no subprocess, no
deserialization. The attack surface is intentionally small.

## Supported versions

| Version | Supported |
|---|:---:|
| `main` branch | ✅ |
| Latest minor release (0.x) | ✅ |
| Older releases | ❌ |

Pre-1.0.0 — only the latest minor receives security fixes.

## Reporting a vulnerability

### Preferred path — GitHub Security Advisory (private)

Open a **private** advisory at
[github.com/codechu/codechu-fmt-py/security/advisories/new](https://github.com/codechu/codechu-fmt-py/security/advisories/new).

### Alternative — Email

Write to `security@codechu.com`.

## Scope — what to report

**In scope:**

- Inputs that crash the formatter (uncaught exceptions for valid
  floats / ints).
- Format-string injection (any path where caller input becomes part
  of an f-string format spec).
- Resource exhaustion: bounded-time formatting must stay bounded
  regardless of magnitude (very large numbers should not loop
  unboundedly).

**Out of scope:**

- Display ambiguity (e.g. "`1.5 MB/s` could mean MiB or MB") — that's
  a documentation issue, not a vulnerability.
- Locale-specific rendering preferences — we deliberately render a
  single, locale-independent form.

## Process

Reports are reviewed on a best-effort basis — no fixed SLA. We aim
for coordinated disclosure within **90 days** of the report.

Public disclosure is coordinated after the fix is released.

## Public disclosure

Once a confirmed fix is released:

- A summary is added to the CHANGELOG under the `### Security`
  category.
- A GitHub Security Advisory is published.
- If a CVE was assigned, its number is referenced.
