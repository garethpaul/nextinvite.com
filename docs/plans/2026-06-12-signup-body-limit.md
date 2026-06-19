# Signup Body Limit

status: completed

## Context

`SignUpHandler.post()` reads the email argument without an application-level
request body ceiling. Email validation caps the normalized address at 254
characters, but an oversized form body can still reach handler parsing before
that field validation runs.

## Priorities

1. Reject signup request bodies larger than 4 KiB before argument access.
2. Return a generic `413` response without echoing submitted content.
3. Preserve XSRF handling, email validation, and idempotent persistence.
4. Protect guard ordering with the dependency-free static checker.

## Implementation Units

### Signup Handler

File: `next/server.py`

Define a 4 KiB body ceiling and check `self.request.body` before calling
`get_argument`. Treat a missing body as empty and return `request too large`
for overflow.

### Static Contract And Documentation

Files:

- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-signup-body-limit.md`

Require the size, status, generic error, and pre-argument ordering. Document
that the guard bounds application handling rather than upstream transport
buffering.

## Verification

Completed locally on 2026-06-12:

- `python3 -m py_compile scripts/check-baseline.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hostile mutations changing the limit or 413 response, or moving argument
  access before the guard, were each rejected by the static contract
- `git diff --check`

Completed on GitHub Actions for implementation head
`7f603f87d06aed9b64770aaf9337fb38eaad6f7b`:

- push run `27397751878`: success
- pull-request run `27397752986`: success

## Boundaries

- Do not include submitted email or body content in errors.
- Do not weaken XSRF, email, or persistence contracts.
- Do not claim to change App Engine or Tornado transport buffering.
