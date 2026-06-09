# Signup Email Length Boundary

status: completed

## Context

NextInvite stores invite signup email addresses in the App Engine datastore.
The route already normalized input and rejected malformed addresses, but it did
not bound the accepted address length before persistence.

## Objectives

- Preserve the existing `/signup` route behavior for valid email addresses.
- Reject addresses longer than the conventional 254-character email boundary.
- Expose the same boundary through the browser email input.
- Extend `make check` with 254-character acceptance and 255-character rejection
  coverage.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
