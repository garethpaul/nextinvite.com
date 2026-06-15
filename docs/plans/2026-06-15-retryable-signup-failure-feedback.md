# Preserve the Signup Form After Retryable Failures

Status: Completed

## Problem

The signup lifecycle releases its page-local ownership flag after completed
HTTP failures, request timeouts, and synchronous setup failures. Each path then
calls `set_text('signup', ...)`, which replaces the entire signup container and
removes the form. The state says a retry is allowed, but the page no longer
contains a control that can perform one.

## Requirements

- Keep the email form and request control present after every retryable
  completed-request, timeout, and synchronous setup failure.
- Render generic text-only feedback in a dedicated alert region without
  exposing response bodies, exception details, or private signup data.
- Clear stale failure feedback only after a new request acquires ownership.
- Preserve duplicate-submission suppression, finite timeout behavior, XSRF
  serialization, successful terminal replacement, backend validation, and
  deterministic datastore idempotency.
- Add ordered, mutation-sensitive portable contracts and matching maintainer
  guidance.

## Implementation Units

### U1: Retryable feedback surface

Files:

- `next/templates/home.html`

Add a dedicated accessible feedback element inside the signup container. Route
all retryable failure messages to that element, clear it when an accepted retry
starts, and keep successful completion targeted at the parent signup container.

### U2: Static regression contracts

Files:

- `scripts/check-baseline.py`

Require the feedback element, accessibility semantics, post-ownership clearing,
all three failure paths, and the separation between retryable feedback and
terminal success replacement.

### U3: Guidance and evidence

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-15-retryable-signup-failure-feedback.md`

Document the retryability boundary and record exact completed verification.

## Verification

- Run focused template/checker contracts, every repository Make gate, and the
  absolute Makefile gate from an external directory.
- Reject isolated mutations that remove the alert element, accessibility
  semantics, retry-start clearing, any failure routing, success/failure target
  separation, guidance, or completed-plan evidence.
- Audit checker compilation, exact diff, whitespace, generated artifacts,
  credential patterns, conflict markers, binaries, large files, and intended
  paths before commit.

## Risks

- Static Linux validation cannot execute the retired App Engine application or
  a browser; the canonical hosted baseline remains the authoritative portable
  contract check.
- The generic message intentionally does not distinguish validation, transport,
  timeout, or setup failures.
- This change must remain stacked on PR #9 and retain base-first ordering.

## Work Completed

- Added a dedicated text-only alert region inside the signup container.
- Centralized retryable failure rendering and routed completed-request, timeout,
  and synchronous setup failures to the alert without replacing the form.
- Cleared stale feedback only after a new request acquires page-local ownership.
- Preserved terminal success replacement and the existing backend boundaries.
- Extended portable contracts and maintainer guidance.

## Verification Completed

- Focused template contracts, checker compilation with external bytecode output,
  and `git diff --check` passed.
- All four Make gates passed from the repository, and `make check` passed from
  an external directory through the absolute Makefile path.
- Nine isolated hostile mutations were rejected: missing feedback region,
  missing accessibility semantics, missing retry-start clearing, each of the
  three failure routes targeting the parent container, success targeting the
  feedback region, missing guidance, and stale plan status.
- Exact intended-path, generated-artifact, credential-pattern, conflict-marker,
  binary, and large-file audits passed.
- No App Engine SDK, datastore, browser, live request, or private signup data
  was used.
