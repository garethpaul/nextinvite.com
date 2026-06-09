# Signup Email Local-Part Validation

status: completed

## Context

Signup email validation normalized addresses, capped total length, rejected
unsafe dot placement, and validated domain labels. The local part before `@`
still accepted broad non-whitespace characters, including unsafe punctuation and
non-ASCII text, before datastore persistence.

## Objectives

- Preserve simple unquoted signup email handling.
- Accept common ASCII local-part characters, including plus tags.
- Reject local parts longer than 64 characters.
- Reject unsafe or non-ASCII local-part characters before datastore writes.
- Extend the SDK-free baseline and docs to preserve local-part validation.

## Verification

- `make check`
- `python3 scripts/check-baseline.py`
- `git diff --check`
