---
title: Signup Network Failure Release
status: planned
date: 2026-06-16
---

# Signup Network Failure Release

## Priority

P1 signup availability. A transport error or browser-aborted request must not
leave the only signup form permanently locked.

## Problem

The signup client releases `invite_request_in_flight` after HTTP failures,
timeouts, and setup exceptions, but does not handle `XMLHttpRequest.onerror` or
`onabort`. Those terminal paths can leave the lock set with no retry feedback.

## Approach

- Introduce one retryable-failure helper that releases the in-flight lock and
  restores the existing sanitized feedback.
- Use it for non-success HTTP completion, timeout, network error, browser abort,
  and synchronous setup/send failure.
- Preserve successful form replacement, semantic form submission, request
  timeout, serialization, XSRF handling, and server behavior.
- Add mutation-sensitive static contracts, maintained guidance, changelog, and
  completed verification evidence.

## Files

- `next/templates/home.html`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-signup-network-failure-release.md`

## Verification

- Prove HTTP failure, timeout, `onerror`, `onabort`, and setup exceptions all
  delegate to the shared release helper.
- Prove success still returns before any failure release.
- Run all repository and external-directory Make gates.
- Reject isolated helper, handler, ordering, guidance, changelog, and completed
  plan mutations.
- Audit the exact diff, generated artifacts, credentials, conflict markers,
  binaries, large files, and whitespace.

## Scope Boundaries

- Do not change request URL, method, content type, timeout duration, payload,
  server validation, datastore behavior, or success copy.
- Do not add dependencies or expose transport diagnostics to visitors.
- Keep PR #11 and its predecessors open and retain base-first stack ordering.

## Success Criteria

- Every retryable terminal XHR failure releases the submission lock and shows
  the existing retry feedback.
- Successful signup behavior remains unchanged.
