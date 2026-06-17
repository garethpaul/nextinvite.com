# Signup Submit Busy State

Status: completed

## Problem

The signup client rejects duplicate submissions while one XHR owns the form,
but the semantic submit button remains enabled. Visitors can repeatedly activate
a control that appears available even though subsequent activations are ignored,
and assistive technology receives no native disabled-state signal.

## Requirements

- Disable the semantic signup submit control only after a new request acquires
  page-local ownership.
- Re-enable the control on every retryable terminal path, but only when the
  releasing request still owns the form.
- Preserve successful terminal form replacement without re-enabling a control
  that is about to be removed.
- Preserve exact request identity, duplicate suppression, timeout, network and
  abort handling, generic feedback, form serialization, XSRF handling, backend
  validation, and deterministic persistence.
- Add ordered, mutation-sensitive portable contracts and synchronized guidance.

## Implementation Units

### U1: Request-owned submit state

Files:

- `next/templates/home.html`
- `next/static/style.css`

Give the existing submit button a stable identifier. Disable it immediately
after signup ownership is acquired and re-enable it inside the exact-request
retry release helper after ownership is cleared. Keep success terminal and
give the disabled control a visible non-interactive affordance.

Test scenarios:

- An accepted submission disables the semantic submit button before XHR setup.
- HTTP failure, timeout, network error, abort, and synchronous setup failure all
  re-enable the button through the exact-request release helper.
- A stale callback cannot re-enable the control for a newer request.
- Success clears ownership and replaces the form without a retry-state release.

### U2: Portable regression contracts

Files:

- `scripts/check-baseline.py`

Require the stable control identifier, post-ownership disable ordering,
identity-before-release ordering, retry-only re-enable behavior, and preservation
of the existing request lifecycle.

Test scenarios:

- All repository and external-directory Make gates accept the implementation.
- Isolated mutations removing the identifier, disable, re-enable, ownership
  ordering, success separation, guidance, or completed evidence are rejected.

### U3: Guidance and evidence

Files:

- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-17-signup-submit-busy-state.md`

Document the request-owned busy-state boundary and record exact completed
verification.

## Validation

- Run checker compilation and all Make aliases from the checkout, plus the
  absolute Makefile check from an external directory.
- Run isolated hostile mutations for source ordering, success separation,
  guidance, and completed-plan requirements.
- Audit the exact diff, generated artifacts, secret signatures, conflict
  markers, binaries, large files, modes, and whitespace before committing.

## Risks

- Portable static validation cannot execute live browser XHR timing or the
  retired App Engine application.
- The control remains disabled after success because the containing form is
  immediately replaced; this is intentional terminal behavior.
- This change is stacked on PR #13, which must remain open and merge first.

## Work Completed

- Added a stable identifier to the semantic submit button and disabled it only
  after an XHR acquired exact page-local ownership.
- Restored the control only through the exact-request retry helper after
  ownership and the in-flight lock were cleared; successful completion remains
  terminal and replaces the form without a retry-state release.
- Added a visible disabled-state affordance and synchronized portable contracts,
  README, security, vision, and change guidance.

## Verification Completed

- All four Make gates passed from the repository, and the absolute Makefile
  check passed from an external directory.
- Nine isolated hostile mutations were rejected across the stable control ID,
  missing and misordered disable behavior, missing and premature re-enable
  behavior, success-path re-enable, disabled styling, README guidance, and
  completed plan status.
- A dependency-free Node runtime harness executed the template JavaScript and
  proved disable-on-ownership, retry re-enable, stale callback isolation, and
  terminal success behavior with a fake DOM and XMLHttpRequest.
- Checker compilation, exact diff review, generated-artifact inspection,
  high-confidence secret-signature scanning, conflict-marker checks, mode,
  binary, large-file, and whitespace audits passed.
- The portable environment did not execute a browser, live XMLHttpRequest,
  retired App Engine runtime, datastore, or production signup service.
