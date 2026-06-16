# Signup Request Ownership

Status: completed

## Problem

One failed XHR can invoke `readystatechange` and then a transport-specific
terminal handler. The first callback releases the global signup lock, allowing
a retry to start, while the later callback can release that newer attempt's
lock because terminal handlers are not bound to the request they belong to.

## Approach

- Retain the active signup XHR alongside the existing in-flight flag.
- Require exact request ownership before success or retryable failure changes
  global signup state.
- Clear request ownership before releasing the lock or rendering terminal
  success.
- Preserve the POST route, form encoding, timeout, generic retry feedback, and
  success-only replacement of the signup form.

## Files

- `next/templates/home.html`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-signup-request-ownership.md`

## Verification Completed

- The focused checker passed. All four Make gates passed from the repository
  root and an external directory.
- Eight isolated hostile mutations were rejected for ownership declaration,
  assignment, success identity, success cleanup, failure identity, handler
  binding, setup failure binding, and completed evidence.
- Exact diff, artifact, credential, conflict-marker, binary, large-file, and
  whitespace audits passed.
- Retired App Engine and browser tooling are unavailable in this environment,
  so end-to-end execution could not be performed.
