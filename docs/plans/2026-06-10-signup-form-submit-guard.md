# Signup Form Submit Guard

status: completed

## Context

The invite form posts through dependency-free JavaScript when the request link
is clicked. The form itself should also route submit events through that handler
so keyboard submissions use the same XSRF-aware, form-encoded request path.

## Objectives

- Route the invite form `submit` event through `request_invite(event)`.
- Preserve the existing click handler and dependency-free XMLHttpRequest path.
- Preserve XSRF form serialization and text-only status updates.
- Extend docs and the active baseline checker for the submit guard.

## Verification

- `scripts/check-baseline.py`
- `make check`
- `git diff --check`
