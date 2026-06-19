# Semantic Signup Submit Control

Status: completed

## Problem

The visible signup action is an anchor with an inline click handler that calls
`request_invite` directly. That path bypasses the form's native email
constraint validation and exposes link semantics for an action. Keyboard form
submission follows the form's submit event instead, so click and keyboard paths
do not share the same browser validation boundary.

## Scope

- Replace the anchor action with a real `button` using `type='submit'`.
- Remove the direct click handler so all accepted submissions flow through the
  form's existing submit event and dependency-free request handler.
- Preserve the existing button classes, visible label, XSRF serialization,
  in-flight guard, timeout handling, retryable failure feedback, and terminal
  success behavior.
- Add minimal button reset styling only where needed to retain the current
  class-driven appearance.
- Extend mutation-sensitive portable contracts and synchronized guidance.

## Files

- `next/templates/home.html`
- `next/static/style.css`
- `scripts/check-baseline.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-15-semantic-signup-submit-control.md`

## Verification

- Run all four repository Make gates and the canonical external-directory
  check without requiring App Engine, datastore, or a live signup request.
- Reject isolated mutations for anchor restoration, missing submit type,
  direct click-handler restoration, lost form handler, styling drift, missing
  guidance, and stale plan status.
- Audit the exact diff, dependencies, generated artifacts, credentials,
  conflicts, binaries, large files, modes, and whitespace.

## Risks

- Browser automation is unavailable unless `agent-browser` is installed; the
  repository's portable contracts remain the local validation boundary.
- Native constraint validation behavior depends on the browser, but using a
  submit button and form submit event is the standards-defined path.
- This change must remain stacked on PR #10; neither pull request may be merged
  or closed without explicit owner authorization.

## Success Criteria

- Pointer and keyboard activation both reach `request_invite` only through the
  form submit event after native constraints pass.
- The visible action exposes button semantics and retains its existing classes
  and label.
- Existing asynchronous ownership, feedback, security, and backend contracts
  remain unchanged.

## Work Completed

- Replaced the direct-action anchor with a semantic submit button while
  retaining the existing classes, label, and form submit handler.
- Removed the click-specific request entry point so native constraints precede
  both pointer and keyboard submissions.
- Added minimal inherited-font and pointer-cursor styling plus mutation-sensitive
  portable contracts and synchronized guidance.

## Verification Completed

- All four Make gates passed from the repository and `make check` passed from
  an external directory.
- Seven isolated hostile mutations were rejected for anchor restoration,
  missing submit type, direct click-handler restoration, lost form routing,
  styling drift, missing guidance, and stale plan status.
- The exact eight-file implementation diff passed dependency, generated-artifact,
  credential, conflict, binary, large-file, mode, whitespace, and intended-path
  audits.
- App Engine, datastore, and live signup requests were not exercised locally;
  browser automation was unavailable because `agent-browser` is not installed.
