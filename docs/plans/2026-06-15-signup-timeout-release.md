# Release Signup Ownership After Request Timeout

Status: In Progress

## Summary

Restore signup retry when an asynchronous browser request never completes by
giving the XHR a finite timeout and releasing the page-local ownership flag
before rendering generic failure feedback.

## Problem

The signup flow releases ownership after completed HTTP failures and
synchronous setup failures, but a request that never reaches `readyState 4`
keeps `invite_request_in_flight` set forever. Every later click or keyboard
submission is then ignored until the page is reloaded.

## Requirements

- Configure a finite timeout after XHR setup and before request dispatch.
- Release the page-local in-flight flag when the timeout fires.
- Render the existing generic text-only failure message after ownership is
  released so the user can retry safely.
- Preserve completed-request failure release, synchronous setup failure
  release, terminal success replacement, XSRF serialization, and backend
  idempotency and validation.
- Add ordered, mutation-sensitive static contracts and matching documentation.

## Implementation

- Define one named signup timeout interval next to the in-flight state.
- Assign that interval to `request.timeout` before `request.send`.
- Add an `ontimeout` callback that releases ownership before rendering the
  existing generic failure message.
- Extend the dependency-free checker, guidance, changelog, and plan evidence.

## Verification

- Run all repository Make gates and external-directory `make check`.
- Reject isolated mutations removing or weakening the timeout constant,
  assignment, callback, release, ordering, documentation, or completed-plan
  status.
- Audit checker syntax, exact diff, whitespace, generated artifacts, conflict
  markers, binary/large files, and changed-line credential patterns.

## Risks

- The timeout may abandon a request whose server-side processing eventually
  succeeds; datastore idempotency keeps a retry for the same normalized email
  from creating a duplicate record.
- No App Engine SDK, datastore, browser, live request, or private signup data is
  available in this environment, so runtime behavior remains unexecuted.
- The change must remain stacked on PR #8; neither pull request may be merged
  or closed without explicit owner authorization.

## Verification Completed

Pending implementation and validation.
