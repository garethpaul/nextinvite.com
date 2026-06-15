# Release Signup Ownership On Setup Failure

Status: Planned

## Summary

Restore signup retry when browser XHR setup or synchronous request dispatch
throws after the page acquires its in-flight flag.

## Problem

The overlap guard correctly acquires ownership before `XMLHttpRequest`
construction, but constructor, `open`, header, serialization, or `send`
exceptions currently escape without clearing that ownership. The page then
ignores every later click or keyboard submission until it is reloaded.

## Requirements

- Catch synchronous XHR construction, setup, serialization, and send failures.
- Clear the page-local in-flight flag before presenting the existing generic
  invalid-signup message.
- Preserve completed-request failure release and terminal success replacement.
- Do not expose exception details or change backend idempotency and validation.
- Add ordered, mutation-sensitive static contracts and matching documentation.

## Implementation

- Wrap XHR construction through `send` in one `try` block after ownership
  acquisition.
- Release ownership and call the existing text-only failure renderer in the
  corresponding `catch` block.
- Extend the dependency-free checker, guidance, changelog, and plan evidence.

## Verification

- Run all repository Make gates and external-directory `make check`.
- Reject isolated mutations removing the catch, ownership release, release
  ordering, generic message, documentation, or completed-plan status.
- Audit checker syntax, exact diff, whitespace, generated artifacts, conflict
  markers, binary/large files, and changed-line credential patterns.

## Risks

- No App Engine SDK, datastore, browser, live request, or private signup data is
  available in this environment, so runtime behavior remains unexecuted.
- The change must remain stacked on PR #7; neither pull request may be merged
  or closed without explicit owner authorization.
